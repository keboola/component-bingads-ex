"""
Covers the optional SOAP envelope capture. The important property under test is that
credentials never reach the log: element contents are substituted, literal token values
are substituted, and an envelope that still contains a secret is withheld entirely.
"""
import logging
import unittest

from bingads_wrapper.soap_logging import (MAX_LOGGED_CHARS, REDACTED, SoapEnvelopeLogger,
                                         attach_soap_debug, find_unknown_credential_elements,
                                         redact)

ACCESS_TOKEN = "EwCAAvBAAUKq3fake-access-token-value-0123456789"
DEVELOPER_TOKEN = "120034G508084627"

ENVELOPE = f"""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header>
    <ns0:DeveloperToken>{DEVELOPER_TOKEN}</ns0:DeveloperToken>
    <ns0:AuthenticationToken>{ACCESS_TOKEN}</ns0:AuthenticationToken>
    <ns0:CustomerId>252471728</ns0:CustomerId>
    <ns0:CustomerAccountId>176201135</ns0:CustomerAccountId>
  </soap:Header>
  <soap:Body><ns0:GetUserRequest><ns0:UserId/></ns0:GetUserRequest></soap:Body>
</soap:Envelope>"""


class FakeOAuthTokens:
    access_token = ACCESS_TOKEN
    refresh_token = "M.C123_fake-refresh-token-value"


class FakeAuthentication:
    oauth_tokens = FakeOAuthTokens()


class FakeAuthorizationData:
    developer_token = DEVELOPER_TOKEN
    authentication = FakeAuthentication()


class FakeContext:
    def __init__(self, envelope=None, reply=None):
        self.envelope = envelope
        self.reply = reply


class TestRedact(unittest.TestCase):

    def test_removes_credential_element_contents(self):
        result = redact(ENVELOPE)
        self.assertNotIn(ACCESS_TOKEN, result)
        self.assertNotIn(DEVELOPER_TOKEN, result)
        self.assertIn(REDACTED, result)

    def test_keeps_non_secret_context(self):
        # Customer/account ids are exactly what makes the envelope useful for diagnosis.
        result = redact(ENVELOPE)
        self.assertIn("252471728", result)
        self.assertIn("176201135", result)
        self.assertIn("GetUserRequest", result)

    def test_removes_literal_secret_outside_known_elements(self):
        leaked = f"<Body>token was {ACCESS_TOKEN}</Body>"
        result = redact(leaked, [ACCESS_TOKEN])
        self.assertIsNotNone(result)
        self.assertNotIn(ACCESS_TOKEN, result)

    def test_removes_xml_escaped_secret_in_text_node(self):
        secret = 'tok&en<value>here'
        leaked = "<Body>tok&amp;en&lt;value&gt;here</Body>"
        result = redact(leaked, [secret])
        self.assertIsNotNone(result)
        self.assertNotIn("tok&amp;en", result)

    def test_removes_quote_escaped_secret_in_attribute(self):
        # Attribute values escape quotes as well as & < >; text nodes do not.
        secret = 'tok&en"value'
        leaked = '<Body attr="tok&amp;en&quot;value"/>'
        result = redact(leaked, [secret])
        self.assertIsNotNone(result)
        self.assertNotIn("tok&amp;en", result)

    def test_short_values_are_not_treated_as_secrets(self):
        # A short or placeholder value would otherwise blank out unrelated text.
        result = redact("<Body>CustomerId 252471728</Body>", ["1"])
        self.assertIn("252471728", result)

    def test_ignores_empty_secrets(self):
        result = redact(ENVELOPE, [None, ""])
        self.assertIsNotNone(result)

    def test_withholds_when_unknown_credential_element_present(self):
        envelope = "<Header><ns0:GoogleIdentityToken>ya29.secret</ns0:GoogleIdentityToken></Header>"
        self.assertIsNone(redact(envelope))


class TestFindUnknownCredentialElements(unittest.TestCase):

    def test_known_elements_are_not_flagged(self):
        self.assertEqual(find_unknown_credential_elements(redact(ENVELOPE)), [])

    def test_unknown_credential_element_is_flagged(self):
        envelope = "<Header><ns0:IdentityProviderToken>abc123</ns0:IdentityProviderToken></Header>"
        self.assertEqual(find_unknown_credential_elements(envelope), ["IdentityProviderToken"])

    def test_empty_element_is_not_flagged(self):
        self.assertEqual(find_unknown_credential_elements("<Header><FutureToken/></Header>"), [])

    def test_non_credential_elements_are_not_flagged(self):
        self.assertEqual(find_unknown_credential_elements(ENVELOPE.replace(ACCESS_TOKEN, "x")
                                                          .replace(DEVELOPER_TOKEN, "y")), [])


class TestSoapEnvelopeLogger(unittest.TestCase):

    def setUp(self):
        self.plugin = SoapEnvelopeLogger(FakeAuthorizationData())

    def assert_no_secrets(self, records):
        blob = "\n".join(r.getMessage() for r in records)
        self.assertNotIn(ACCESS_TOKEN, blob)
        self.assertNotIn(DEVELOPER_TOKEN, blob)
        self.assertNotIn(FakeOAuthTokens.refresh_token, blob)
        return blob

    def test_logs_redacted_request(self):
        with self.assertLogs(level=logging.DEBUG) as captured:
            self.plugin.sending(FakeContext(envelope=ENVELOPE))
        blob = self.assert_no_secrets(captured.records)
        self.assertIn("Bing Ads SOAP request", blob)
        self.assertIn(REDACTED, blob)

    def test_logs_redacted_response(self):
        with self.assertLogs(level=logging.DEBUG) as captured:
            self.plugin.received(FakeContext(reply=ENVELOPE))
        blob = self.assert_no_secrets(captured.records)
        self.assertIn("Bing Ads SOAP response", blob)

    def test_accepts_bytes_payload(self):
        with self.assertLogs(level=logging.DEBUG) as captured:
            self.plugin.received(FakeContext(reply=ENVELOPE.encode("utf-8")))
        self.assert_no_secrets(captured.records)

    def test_truncates_large_envelope(self):
        with self.assertLogs(level=logging.DEBUG) as captured:
            self.plugin.received(FakeContext(reply="<a>" + ("x" * (MAX_LOGGED_CHARS * 2)) + "</a>"))
        self.assertLessEqual(len(captured.records[0].getMessage()), MAX_LOGGED_CHARS + 200)

    def test_empty_payload_logs_nothing(self):
        logger = logging.getLogger()
        previous = logger.level
        logger.setLevel(logging.DEBUG)
        try:
            with self.assertNoLogs(level=logging.DEBUG):
                self.plugin.sending(FakeContext(envelope=None))
        finally:
            logger.setLevel(previous)

    def test_withholds_envelope_with_unknown_credential_element(self):
        # A credential header this module has no substitution rule for, e.g. one Microsoft
        # adds later. The whole envelope must be withheld, not partially logged.
        envelope = "<soap:Header><ns0:GoogleIdentityToken>ya29.secret</ns0:GoogleIdentityToken></soap:Header>"
        with self.assertLogs(level=logging.DEBUG) as captured:
            self.plugin.received(FakeContext(reply=envelope))
        blob = "\n".join(r.getMessage() for r in captured.records)
        self.assertIn("withheld", blob)
        self.assertIn("GoogleIdentityToken", blob)
        self.assertNotIn("ya29.secret", blob)


class FakeSudsClient:
    def __init__(self):
        self.applied = {}

    def set_options(self, **kwargs):
        self.applied.update(kwargs)


class FakeHeaderPlugin:
    """Stands in for the SDK's own HeaderPlugin, which must survive attachment."""


class FakeServiceClient:
    """
    Mimics bingads ServiceClient closely enough to pin the two traps:
    it pre-populates `_options['plugins']` with its own HeaderPlugin, and it replays
    `_options` through `set_options` before every service call.
    """

    def __init__(self):
        self.header_plugin = FakeHeaderPlugin()
        self._options = {"cache": object(), "cachingpolicy": 1, "plugins": [self.header_plugin]}
        self._soap_client = FakeSudsClient()

    def replay_options_before_call(self):
        self._soap_client.set_options(**self._options)


class TestAttachSoapDebug(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger()
        self.previous = self.logger.level
        self.client = FakeServiceClient()

    def tearDown(self):
        self.logger.setLevel(self.previous)

    def attached_plugins(self):
        return [p for p in self.client._soap_client.applied.get("plugins", [])
                if isinstance(p, SoapEnvelopeLogger)]

    def test_no_op_when_not_debug(self):
        self.logger.setLevel(logging.INFO)
        attach_soap_debug(self.client, FakeAuthorizationData())
        self.assertEqual(self.attached_plugins(), [])
        self.assertNotIn("plugins", self.client._soap_client.applied)

    def test_attaches_when_debug(self):
        self.logger.setLevel(logging.DEBUG)
        attach_soap_debug(self.client, FakeAuthorizationData())
        self.assertEqual(len(self.attached_plugins()), 1)

    def test_keeps_sdk_header_plugin(self):
        # get_response_header() breaks if HeaderPlugin is displaced.
        self.logger.setLevel(logging.DEBUG)
        attach_soap_debug(self.client, FakeAuthorizationData())
        self.assertIn(self.client.header_plugin, self.client._soap_client.applied["plugins"])

    def test_survives_pre_call_options_replay(self):
        # ServiceClient.__getattr__ re-applies _options before every call; the plugin has
        # to be in _options or it is silently dropped on first use.
        self.logger.setLevel(logging.DEBUG)
        attach_soap_debug(self.client, FakeAuthorizationData())
        self.client._soap_client.applied.pop("plugins")
        self.client.replay_options_before_call()
        self.assertEqual(len(self.attached_plugins()), 1)

    def test_is_idempotent(self):
        self.logger.setLevel(logging.DEBUG)
        attach_soap_debug(self.client, FakeAuthorizationData())
        attach_soap_debug(self.client, FakeAuthorizationData())
        self.assertEqual(len(self.attached_plugins()), 1)

    def test_never_raises_on_unexpected_client(self):
        self.logger.setLevel(logging.DEBUG)
        attach_soap_debug(object(), FakeAuthorizationData())  # must not raise


if __name__ == "__main__":
    unittest.main()
