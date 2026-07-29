import logging
import re

from keboola.component import UserException

# Microsoft puts a TrackingId in the fault string. It is the only handle Microsoft support
# can act on, and the structured detail below does not repeat it.
TRACKING_ID_PATTERN = re.compile(r"TrackingId:\s*([0-9a-fA-F-]{8,})")


def output_error_message(message):
    logging.error(message)


def get_webfault_error_message(error):
    error_messages = []
    # The numeric Code and symbolic ErrorCode are what actually identify the fault.
    # Without them the message alone is ambiguous: code 105 covers AccountInactive,
    # InvalidAccessToken and UserNotFound, which have entirely different resolutions.
    code = getattr(error, "Code", None)
    if code is not None:
        error_messages.append(f"Code: {code}")
    error_code = getattr(error, "ErrorCode", None)
    if error_code:
        error_messages.append(f"ErrorCode: {error_code}")
    # OperationError/BatchError use "Details" (plural); AdApiError uses "Detail" (singular).
    # Only "Details" was read before, so every AdApiError - including all authentication
    # failures - lost its detail text.
    for detail_attribute in ("Details", "Detail"):
        detail = getattr(error, detail_attribute, None)
        if detail:
            error_messages.append(f"{detail}")
    if hasattr(error, "Message"):
        error_messages.append(f"{error.Message}")
    if hasattr(error, "FieldPath"):
        error_messages.append(f"FieldPath: {error.FieldPath}")
    if not error_messages:
        error_messages = [f"{e[0]}: {str(e[1])}" for e in error]
    return ' | '.join(error_messages)


def get_tracking_id(fault) -> str:
    """Extract Microsoft's TrackingId from the fault string, if it carries one."""
    faultstring = getattr(fault, "faultstring", None)
    if not faultstring:
        return ""
    match = TRACKING_ID_PATTERN.search(str(faultstring))
    return match.group(1) if match else ""


def get_error_detail_string(error_detail, error_attribute_set) -> str:
    api_errors = error_detail
    for _field in error_attribute_set:
        api_errors = getattr(api_errors, _field, None)
    if api_errors is None:
        return ""

    if isinstance(api_errors, list):
        error_string = '\n'.join([get_webfault_error_message(api_error) for api_error in api_errors])
    else:
        error_string = get_webfault_error_message(api_errors)
    return error_string


def process_webfault_errors(ex):
    if not hasattr(ex.fault, "detail"):
        raise UserException(ex.fault.faultstring)

    # WTF?
    error_attribute_sets = (
        ["ApiFault", "OperationErrors", "OperationError"],
        ["AdApiFaultDetail", "Errors", "AdApiError"],
        ["ApiFaultDetail", "BatchErrors", "BatchError"],
        ["ApiFaultDetail", "OperationErrors", "OperationError"],
        ["EditorialApiFaultDetail", "BatchErrors", "BatchError"],
        ["EditorialApiFaultDetail", "EditorialErrors", "EditorialError"],
        ["EditorialApiFaultDetail", "OperationErrors", "OperationError"],
    )

    errors = []

    for error_attribute_set in error_attribute_sets:
        error = get_error_detail_string(ex.fault.detail, error_attribute_set)
        if error:
            errors.append(error)
            break

    # Handle serialization errors, for example:
    # The formatter threw an exception while trying to deserialize the message, etc.
    if not errors and hasattr(ex.fault, "detail") and hasattr(ex.fault.detail, "ExceptionDetail"):
        api_errors = ex.fault.detail.ExceptionDetail
        if isinstance(api_errors, list):
            for api_error in api_errors:
                errors.append(api_error.Message)
        else:
            errors.append(api_errors.Message)

    error_message = '\n'.join(errors)

    # The detail branch above never looks at the fault string, so without this the
    # TrackingId is lost as soon as a fault carries structured detail.
    tracking_id = get_tracking_id(ex.fault)
    if tracking_id:
        error_message = f"{error_message} | TrackingId: {tracking_id}" if error_message \
            else f"TrackingId: {tracking_id}"

    raise UserException(error_message) from ex
