import logging


def output_error_message(message):
    logging.error(message)


def output_bing_ads_webfault_error(error):
    if hasattr(error, "ErrorCode"):
        output_error_message("ErrorCode: {0}".format(error.ErrorCode))
    if hasattr(error, "Code"):
        output_error_message("Code: {0}".format(error.Code))
    if hasattr(error, "Details"):
        output_error_message("Details: {0}".format(error.Details))
    if hasattr(error, "FieldPath"):
        output_error_message("FieldPath: {0}".format(error.FieldPath))
    if hasattr(error, "Message"):
        output_error_message("Message: {0}".format(error.Message))
    output_error_message("")


def output_error_detail(error_detail, error_attribute_set):
    api_errors = error_detail
    for _field in error_attribute_set:
        api_errors = getattr(api_errors, _field, None)
    if api_errors is None:
        return False
    if isinstance(api_errors, list):
        for api_error in api_errors:
            output_bing_ads_webfault_error(api_error)
    else:
        output_bing_ads_webfault_error(api_errors)
    return True


def output_webfault_errors(ex):
    if not hasattr(ex.fault, "detail"):
        raise Exception("Unknown WebFault")

    error_attribute_sets = (
        ["ApiFault", "OperationErrors", "OperationError"],
        ["AdApiFaultDetail", "Errors", "AdApiError"],
        ["ApiFaultDetail", "BatchErrors", "BatchError"],
        ["ApiFaultDetail", "OperationErrors", "OperationError"],
        ["EditorialApiFaultDetail", "BatchErrors", "BatchError"],
        ["EditorialApiFaultDetail", "EditorialErrors", "EditorialError"],
        ["EditorialApiFaultDetail", "OperationErrors", "OperationError"],
    )

    for error_attribute_set in error_attribute_sets:
        if output_error_detail(ex.fault.detail, error_attribute_set):
            return

    # Handle serialization errors, for example:
    # The formatter threw an exception while trying to deserialize the message, etc.
    if hasattr(ex.fault, "detail") and hasattr(ex.fault.detail, "ExceptionDetail"):
        api_errors = ex.fault.detail.ExceptionDetail
        if isinstance(api_errors, list):
            for api_error in api_errors:
                output_error_message(api_error.Message)
        else:
            output_error_message(api_errors.Message)
        return

    raise Exception("Unknown WebFault")
