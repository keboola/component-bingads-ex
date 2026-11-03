import json
import logging

from keboola.component import UserException

# Microsoft returns its API errors in these collections. The REST API uses the same
# error names as the SOAP faults did, but delivers them as JSON instead of a fault tree.
ERROR_COLLECTION_KEYS = (
    "OperationErrors",
    "Errors",
    "BatchErrors",
    "EditorialErrors",
    "InvalidAdGroupIds",
    "NestedPartialErrors",
)

# Fields of one error object, in the order the message shows them.
ERROR_DETAIL_FIELDS = ("Details", "Message", "FieldPath")


def output_error_message(message):
    logging.error(message)


def get_api_error_message(error) -> str:
    """
    Build a readable message for one error object.

    The SOAP build received ``suds`` objects here. The REST build receives dictionaries
    decoded from the JSON error body. Both shapes are accepted, so the message format
    does not change for the user.
    """
    error_messages = []
    for field in ERROR_DETAIL_FIELDS:
        value = error.get(field) if isinstance(error, dict) else getattr(error, field, None)
        if value in (None, ""):
            continue
        error_messages.append(f"FieldPath: {value}" if field == "FieldPath" else f"{value}")

    if error_messages:
        return " | ".join(error_messages)

    if isinstance(error, dict):
        return " | ".join(f"{key}: {value}" for key, value in error.items() if value not in (None, ""))
    return str(error)


def _decode_error_body(exception) -> dict:
    """Decode the JSON body of an API exception. Returns an empty dict if it is not JSON."""
    body = getattr(exception, "body", None)
    if body is None:
        data = getattr(exception, "data", None)
        return data if isinstance(data, dict) else {}
    if isinstance(body, bytes):
        body = body.decode("utf-8", errors="replace")
    if isinstance(body, dict):
        return body
    try:
        decoded = json.loads(body)
    except (ValueError, TypeError):
        return {}
    return decoded if isinstance(decoded, dict) else {}


def _collect_errors(payload: dict) -> list[str]:
    """Collect every error message held in the known error collections of ``payload``."""
    messages = []
    for key in ERROR_COLLECTION_KEYS:
        errors = payload.get(key)
        if not errors:
            continue
        if isinstance(errors, dict):
            errors = [errors]
        if not isinstance(errors, list):
            continue
        for error in errors:
            message = get_api_error_message(error)
            if message:
                messages.append(message)
    return messages


def process_api_errors(exception):
    """
    Turn an API error into a ``UserException`` that names what the API rejected.

    Replaces the SOAP fault handler. The SOAP build walked a fault tree
    (``ex.fault.detail.ApiFault.OperationErrors.OperationError``). The REST API returns
    a JSON body instead, so the error collections are read from that body.
    """
    payload = _decode_error_body(exception)
    messages = _collect_errors(payload)

    # Some failures report a single message at the top level rather than a collection.
    if not messages:
        for key in ("Message", "message", "error_description", "FaultString"):
            value = payload.get(key)
            if value:
                messages.append(str(value))
                break

    if not messages:
        # Nothing recognisable in the body. Keep the HTTP status and the raw body so the
        # failure stays diagnosable instead of being reported as an empty message.
        status = getattr(exception, "status", None)
        reason = getattr(exception, "reason", None)
        raw_body = getattr(exception, "body", None)
        parts = [part for part in (f"HTTP {status}" if status else None, reason, raw_body) if part]
        messages.append(" | ".join(str(part) for part in parts) or str(exception))

    raise UserException("\n".join(messages)) from exception
