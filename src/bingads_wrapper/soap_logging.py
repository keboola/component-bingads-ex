"""
Optional capture of the raw Bing Ads SOAP traffic, for diagnosing API faults.

`error_handling` already surfaces the structured parts of a fault (`AdApiError.Code`,
`ErrorCode`, `Detail`). This module is the fallback for when even those do not tell
two causes apart, and logs the envelopes themselves.

It stays off unless the configuration sets `"debug": true`, which is what puts the
root logger at DEBUG.

Credentials travel in the SOAP header (`AuthenticationToken`, `DeveloperToken`), so an
envelope is never logged as it arrived. Two layers handle that:

1. The contents of every known credential element are substituted, and the literal token
   values are substituted wherever else they appear.
2. The envelope is then scanned for credential-looking elements this module does not know
   about. If one turns up, the envelope is withheld rather than logged - better to lose a
   diagnostic than to leak a header Microsoft added after this was written.
"""
import logging
import re
from typing import Iterable, Iterator, Optional
from xml.sax.saxutils import escape as xml_escape

from suds.plugin import MessagePlugin

REDACTED = "***REDACTED***"

# SOAP header elements known to carry credentials.
SECRET_ELEMENTS = ("AuthenticationToken", "DeveloperToken", "UserName", "Password")

# Element names matching this are assumed to hold something sensitive.
CREDENTIAL_NAME_PATTERN = re.compile(r"token|password|secret|credential|assertion", re.IGNORECASE)

# Report definitions and bulk payloads can be very large; cap what reaches the log.
MAX_LOGGED_CHARS = 20000

# Below this length a value is too generic to search for safely (empty or placeholder).
MIN_SECRET_LENGTH = 8

_SECRET_ELEMENT_PATTERNS = tuple(
    re.compile(rf"(<(?:\w+:)?{element}\b[^>]*>)(.*?)(</(?:\w+:)?{element}>)", re.DOTALL)
    for element in SECRET_ELEMENTS
)

# Opening tags with a non-empty body, so `<Foo/>` and `<Foo></Foo>` are not flagged.
_NON_EMPTY_ELEMENT_PATTERN = re.compile(r"<(?:\w+:)?(\w+)\b[^>/]*>(?!\s*<)([^<]+)</")


def _secret_variants(secret: str) -> Iterator[str]:
    """
    Yield the forms a secret can take inside an envelope.

    Text nodes escape only `&`, `<` and `>`; attribute values additionally escape quotes.
    Both forms are produced so neither placement can slip through.
    """
    seen = set()
    for candidate in (secret,
                      xml_escape(secret),
                      xml_escape(secret, {'"': "&quot;", "'": "&apos;"})):
        if candidate not in seen:
            seen.add(candidate)
            yield candidate


def _usable_secrets(literal_secrets: Iterable[str]) -> list[str]:
    return [s for s in literal_secrets if s and len(s) >= MIN_SECRET_LENGTH]


def find_unknown_credential_elements(envelope: str) -> list[str]:
    """
    Names of populated, credential-looking elements that are not in SECRET_ELEMENTS.

    This is what makes the withholding guard reachable: it catches a sensitive header
    this module has no substitution rule for, rather than re-checking values that were
    already substituted.
    """
    unknown = []
    for name, body in _NON_EMPTY_ELEMENT_PATTERN.findall(envelope):
        if name in SECRET_ELEMENTS or REDACTED in body:
            continue
        if CREDENTIAL_NAME_PATTERN.search(name) and name not in unknown:
            unknown.append(name)
    return unknown


def redact(envelope: str, literal_secrets: Iterable[str] = ()) -> Optional[str]:
    """
    Remove credentials from a SOAP envelope.

    Returns the redacted envelope, or None when it holds a credential-looking element
    this module cannot redact - in that case the caller must not log the envelope.
    """
    for pattern in _SECRET_ELEMENT_PATTERNS:
        envelope = pattern.sub(rf"\g<1>{REDACTED}\g<3>", envelope)

    for secret in _usable_secrets(literal_secrets):
        for variant in _secret_variants(secret):
            envelope = envelope.replace(variant, REDACTED)

    if find_unknown_credential_elements(envelope):
        return None

    return envelope


class SoapEnvelopeLogger(MessagePlugin):
    """
    suds plugin logging redacted SOAP envelopes at DEBUG level.

    The authorization data is kept rather than the token values, because the access
    token is refreshed during a run and the redaction has to see the current one.
    """

    def __init__(self, authorization_data=None):
        self._authorization_data = authorization_data

    def sending(self, context):
        self._log("Bing Ads SOAP request", context.envelope)

    def received(self, context):
        self._log("Bing Ads SOAP response", context.reply)

    def _literal_secrets(self) -> tuple:
        authorization_data = self._authorization_data
        if authorization_data is None:
            return ()
        oauth_tokens = getattr(getattr(authorization_data, "authentication", None), "oauth_tokens", None)
        return tuple(
            secret for secret in (
                getattr(authorization_data, "developer_token", None),
                getattr(oauth_tokens, "access_token", None),
                getattr(oauth_tokens, "refresh_token", None),
            ) if secret
        )

    def _log(self, label: str, payload) -> None:
        if not payload:
            return
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8", errors="replace")
        payload = str(payload)
        redacted = redact(payload, self._literal_secrets())
        if redacted is None:
            unknown = find_unknown_credential_elements(payload)
            logging.warning(
                f"{label} withheld: no redaction rule for element(s) {', '.join(unknown)}. "
                f"Add them to SECRET_ELEMENTS in soap_logging.py to make this envelope loggable.")
            return
        logging.debug(f"{label}: {redacted[:MAX_LOGGED_CHARS]}")


# suds logs the whole parsed WSDL at DEBUG - tens of thousands of lines per service, which
# would bury the envelopes we actually want and hit the job-log ingestion limits. Its own
# loggers are pinned above DEBUG so only this module's targeted output gets through.
SUDS_LOGGER_ROOT = "suds"
SUDS_LOG_LEVEL = logging.WARNING


def debug_enabled() -> bool:
    """True when the configuration asked for verbose logging (`"debug": true`)."""
    return logging.getLogger().isEnabledFor(logging.DEBUG)


def silence_suds_logging() -> None:
    """
    Keep suds' own DEBUG output out of the log.

    suds modules use `getLogger(__name__)`, so they are children of `suds` and inherit this
    level as long as they have none of their own (they do not).
    """
    logging.getLogger(SUDS_LOGGER_ROOT).setLevel(SUDS_LOG_LEVEL)


def attach_soap_debug(service_client, authorization_data=None) -> None:
    """
    Attach redacted envelope logging to a `bingads` ServiceClient. No-op unless debug is on.

    Passing `plugins=` to the ServiceClient constructor does NOT work: it assigns
    `suds_options['plugins'] = [HeaderPlugin()]` unconditionally, discarding anything the
    caller supplied. It also replays `self._options` through `set_options` before every
    service call, so the plugin has to live in `_options` too or it is dropped again on
    first use. Hence appending to the existing list in both places, keeping the SDK's own
    HeaderPlugin - `get_response_header()` depends on it.
    """
    if not debug_enabled():
        return
    try:
        plugins = list(service_client._options.get("plugins") or [])
        if any(isinstance(plugin, SoapEnvelopeLogger) for plugin in plugins):
            return
        plugins.append(SoapEnvelopeLogger(authorization_data))
        service_client._options["plugins"] = plugins
        service_client._soap_client.set_options(plugins=plugins)
    except Exception as ex:
        # Diagnostics must never break an extraction.
        logging.debug(f"Could not attach SOAP envelope logging: {ex}")


# Applied on import, not inside attach_soap_debug: suds emits the WSDL dump while the
# ServiceClient is being constructed, which is before anything can be attached to it.
# Importing this module is what guarantees the level is set in time.
silence_suds_logging()
