from dataclasses import dataclass, field
from typing import List
from datetime import date

from suds.sudsobject import Object

from bingads.service_client import ServiceClient, AuthorizationData
from bingads.v13.reporting import ReportingDownloadParameters

KEY_AGGREGATION = "aggregation"
KEY_REPORT_TYPE = "report_type"
KEY_FORMAT_VERSION = "format_version"
KEY_RETURN_ONLY_COMPLETE_DATA = "return_only_complete_data"
KEY_TIME = "time"
KEY_TIME_ZONE = "time_zone"
KEY_PREDEFINED_TIME = "predefined_time"
KEY_DATE_RANGE_START = "date_range_start"
KEY_DATE_RANGE_END = "date_range_end"
KEY_COLUMNS = "columns"

DOWNLOAD_REQUEST_TIMEOUT_PERIOD_MILLISECONDS = 60 * 1000
OVERWRITE_RESULT_FILE = True

EXCLUDE_COLUMNS_HEADERS = False
EXCLUDE_REPORT_FOOTER = True
EXCLUDE_REPORT_HEADER = True


@dataclass(slots=True)
class ReportingDownloadParametersFactory:
    reporting_service: ServiceClient
    config_dict: dict
    result_file_directory: str
    result_file_name: str
    report_file_format: str

    _authorization_data: AuthorizationData = field(init=False)
    _report_type: str = field(init=False)
    _report_request: Object = field(init=False)

    def __post_init__(self):
        self._authorization_data = self.reporting_service.authorization_data
        self._report_type: str = self.config_dict[KEY_REPORT_TYPE]
        self._report_request = self.reporting_service.factory.create(
            self._report_type + "ReportRequest"
        )
        self._create_report_request()

    def create(self) -> ReportingDownloadParameters:
        return ReportingDownloadParameters(
            report_request=self._report_request,
            result_file_directory=self.result_file_directory,
            result_file_name=self.result_file_name,
            overwrite_result_file=OVERWRITE_RESULT_FILE,
            timeout_in_milliseconds=DOWNLOAD_REQUEST_TIMEOUT_PERIOD_MILLISECONDS,
        )

    def _create_report_request(self):
        self._set_report_request_base_parameters()
        if hasattr(self._report_request, "Time"):
            self._set_report_request_time_parameter()
        if hasattr(self._report_request, "Columns"):
            self._set_report_request_columns_parameter()
        if hasattr(self._report_request, "Aggregation"):
            self._set_report_request_aggregation_parameter()
        if hasattr(self._report_request, "Scope"):
            self._set_report_request_scope_parameter()

    def _set_report_request_base_parameters(self):
        self._report_request.ExcludeColumnHeaders = EXCLUDE_COLUMNS_HEADERS
        self._report_request.ExcludeReportFooter = EXCLUDE_REPORT_FOOTER
        self._report_request.ExcludeReportHeader = EXCLUDE_REPORT_HEADER
        self._report_request.Format.set(self.report_file_format)
        self._report_request.FormatVersion = self.config_dict[KEY_FORMAT_VERSION]
        self._report_request.ReturnOnlyCompleteData: bool = self.config_dict[
            KEY_RETURN_ONLY_COMPLETE_DATA
        ]

    def _set_report_request_aggregation_parameter(self):
        self._report_request.Aggregation.set(self.config_dict[KEY_AGGREGATION])

    def _set_report_request_time_parameter(self):  # TODO: finish
        time = self._report_request.Time
        time_dict: dict = self.config_dict[KEY_TIME]

        time.ReportTimeZone.set(time_dict[KEY_TIME_ZONE])
        if time_dict.get(KEY_PREDEFINED_TIME):
            time.PredefinedTime = time_dict[KEY_PREDEFINED_TIME]
            time.CustomDateRangeStart = None
            time.CustomDateRangeEnd = None
        else:
            start_date = date.fromisoformat(time_dict[KEY_DATE_RANGE_START])
            end_date = date.fromisoformat(time_dict[KEY_DATE_RANGE_END])
            time.CustomDateRangeStart.Year = start_date.year
            time.CustomDateRangeStart.Month = start_date.month
            time.CustomDateRangeStart.Day = start_date.day
            time.CustomDateRangeEnd.Year = end_date.year
            time.CustomDateRangeEnd.Month = end_date.month
            time.CustomDateRangeEnd.Day = end_date.day

    def _set_report_request_columns_parameter(self):  # TODO: finish
        report_columns = self._report_request.Columns
        column_array: List[str] = getattr(
            report_columns, self._report_type + "ReportColumn"
        )
        column_names: List[str] = self.config_dict[KEY_COLUMNS]
        column_array.extend(column_names)

    def _set_report_request_scope_parameter(self):
        self._report_request.Scope.AccountIds = {
            "long": [self._authorization_data.account_id]
        }
