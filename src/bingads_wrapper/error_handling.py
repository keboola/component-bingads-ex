import logging

from keboola.component import UserException


def output_error_message(message):
    logging.error(message)


def get_webfault_error_message(error):
    error_messages = []
    if hasattr(error, "Details"):
        error_messages.append(f"{error.Details}")
    if hasattr(error, "Message"):
        error_messages.append(f"{error.Message}")
    if hasattr(error, "FieldPath"):
        error_messages.append(f"FieldPath: {error.FieldPath}")
    if not error_messages:
        error_messages = [f"{e[0]}: {str(e[1])}" for e in error]
    return ' | '.join(error_messages)


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
    raise UserException(error_message) from ex
