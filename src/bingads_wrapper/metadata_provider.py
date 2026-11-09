"""
Lists of report columns and bulk entities, used by the configuration sync actions.

The SOAP build read these from the WSDL proxy files that the SDK shipped
(``bingads/v13/proxies/production/*.xml``). The REST SDK does not ship those files.
The same values are now published as generated enums in ``openapi_client.models``,
so they are read from there. The returned shapes are unchanged.
"""

import openapi_client.models as rest_models

REPORT_REQUEST_SUFFIX = "ReportRequest"
REPORT_COLUMN_SUFFIX = "ReportColumn"


def get_report_available_columns() -> dict:
    """
    Map each report type to the column names it supports.

    The key is the report type without the "ReportRequest" suffix, which is the same key
    the SOAP build produced. Only report types that the SDK declares columns for are
    listed, matching the old behaviour of skipping a type with an empty column list.
    """
    result_dict = {}
    for attribute_name in dir(rest_models):
        if not attribute_name.endswith(REPORT_REQUEST_SUFFIX):
            continue
        report_type = attribute_name[: -len(REPORT_REQUEST_SUFFIX)]

        column_enum = getattr(rest_models, f"{report_type}{REPORT_COLUMN_SUFFIX}", None)
        if column_enum is None:
            continue

        column_names = [member.value for member in column_enum]
        if not column_names:
            continue

        result_dict[report_type] = column_names

    return result_dict


def get_available_bulk_entities() -> list:
    """
    Return the names of the entities that the Bulk service can download.

    The REST enum carries a "None" placeholder that the SOAP definition did not expose.
    It is not a downloadable entity, so it stays out of the list the configuration shows.
    """
    return [member.value for member in rest_models.DownloadEntity if member.value != "None"]
