import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from bingads.service_client import ServiceClient, AuthorizationData
from bingads.v13.reporting import ReportingDownloadParameters
from dateparser import parse
from keboola.component.exceptions import UserException
from suds.sudsobject import Object

from .prebuilt_configs import get_prebuilt_report_config
from .utils import comma_separated_str_to_list

KEY_PRESET_NAME = "preset_name"
KEY_AGGREGATION = "aggregation"
KEY_REPORT_TYPE = "report_type"
KEY_FORMAT_VERSION = "format_version"
KEY_RETURN_ONLY_COMPLETE_DATA = "return_only_complete_data"
KEY_TIME_RANGE = "time_range"
KEY_COLUMNS = "columns"
KEY_PRIMARY_KEY = "primary_key"
KEY_COLUMNS_ARRAY = "columns_array"
KEY_PRIMARY_KEY_ARRAY = "primary_key_array"

# Time range keys:
KEY_TIME_ZONE = "time_zone"
KEY_PERIOD = "period"
KEY_DATE_RANGE_START = "date_from"
KEY_DATE_RANGE_END = "date_to"

DOWNLOAD_REQUEST_TIMEOUT_PERIOD_MILLISECONDS = 60 * 1000
OVERWRITE_RESULT_FILE = True

EXCLUDE_COLUMNS_HEADERS = False
EXCLUDE_REPORT_FOOTER = True
EXCLUDE_REPORT_HEADER = True
DEFAULT_FORMAT_VERSION = "2.0"


@dataclass(slots=True)
class ReportingDownloadParametersFactory:
    reporting_service: ServiceClient
    config_dict: dict[str, str | list[str]]
    result_file_directory: str
    report_file_format: str

    result_file_name: Optional[str] = None
    last_sync_time_in_utc: Optional[datetime] = None

    primary_key: list[str] = field(init=False)

    _authorization_data: AuthorizationData = field(init=False)
    _report_type: str = field(init=False)
    _report_request: Object = field(init=False)

    def __post_init__(self):
        self._authorization_data = self.reporting_service.authorization_data
        config_keys = set(self.config_dict.keys())
        missing_config_dict_keys = {KEY_REPORT_TYPE, KEY_COLUMNS_ARRAY, KEY_PRIMARY_KEY_ARRAY} - config_keys

        # for backward compatibility
        try:
            if KEY_COLUMNS in config_keys and KEY_PRIMARY_KEY in config_keys:
                missing_config_dict_keys.remove(KEY_COLUMNS_ARRAY)
                missing_config_dict_keys.remove(KEY_PRIMARY_KEY_ARRAY)
        except KeyError:
            pass

        if missing_config_dict_keys:
            if KEY_PRESET_NAME not in self.config_dict:
                raise UserException(
                    f"Preset name must be specified if {KEY_REPORT_TYPE}, {KEY_COLUMNS_ARRAY} "
                    f"or {KEY_PRIMARY_KEY_ARRAY}"
                    f" is not present in report settings.")
            missing_config_dict_keys_str = ", ".join(missing_config_dict_keys)
            logging.info(
                f"Since these keys were not present in report settings: {missing_config_dict_keys_str},"
                f" trying to find a prebuilt config using specified preset name ({self.config_dict[KEY_PRESET_NAME]}).")
            self.config_dict = self.config_dict | get_prebuilt_report_config(
                preset_name=self.config_dict[KEY_PRESET_NAME], aggregation=self.config_dict[KEY_AGGREGATION])
        if not self.result_file_name:
            if KEY_PRESET_NAME in self.config_dict:
                self.result_file_name = (f"{self.config_dict[KEY_PRESET_NAME]}_"
                                         f"{self.config_dict[KEY_AGGREGATION]}_Report.csv")
            else:
                self.result_file_name = f"{self.config_dict[KEY_REPORT_TYPE]}_Report.csv"
        self._report_type: str = self.config_dict[KEY_REPORT_TYPE]
        self._report_request = self.reporting_service.factory.create(self._report_type + "ReportRequest")
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
            self._set_report_request_columns_parameter_and_primary_key()
        if hasattr(self._report_request, "Aggregation"):
            self._set_report_request_aggregation_parameter()
        if hasattr(self._report_request, "Scope"):
            self._set_report_request_scope_parameter()

    def _set_report_request_base_parameters(self):
        self._report_request.ExcludeColumnHeaders = EXCLUDE_COLUMNS_HEADERS
        self._report_request.ExcludeReportFooter = EXCLUDE_REPORT_FOOTER
        self._report_request.ExcludeReportHeader = EXCLUDE_REPORT_HEADER
        self._report_request.Format.set(self.report_file_format)
        self._report_request.FormatVersion = self.config_dict.get(KEY_FORMAT_VERSION, DEFAULT_FORMAT_VERSION)
        self._report_request.ReturnOnlyCompleteData: bool = self.config_dict[KEY_RETURN_ONLY_COMPLETE_DATA]

    def _set_report_request_aggregation_parameter(self):
        self._report_request.Aggregation.set(self.config_dict[KEY_AGGREGATION])

    def _set_report_request_time_parameter(self):
        time = self._report_request.Time
        time_dict: dict = self.config_dict[KEY_TIME_RANGE]
        time_zone = time_dict[KEY_TIME_ZONE]
        period = time_dict[KEY_PERIOD]

        time.ReportTimeZone.set(time_zone)
        if period == "CustomTimeRange":
            if time_dict[KEY_DATE_RANGE_START] == "last run":
                if not self.last_sync_time_in_utc:
                    raise UserException(
                        'Date To specified as "last run", but no previous run sync time is available'
                        ' (probably because this is the first run of this configuration row).'
                        ' Please specify the Date To Time Range parameter as an absolute date (e.g. "2022-09-10"),'
                        ' or a relative date (e.g. "1 year ago").')
                start_date = self.last_sync_time_in_utc
            else:
                start_date = parse(time_dict[KEY_DATE_RANGE_START])
            end_date = parse(time_dict[KEY_DATE_RANGE_END])
            if not start_date:
                raise UserException("Date From could not be parsed.")
            if not end_date:
                raise UserException("Date To could not be parsed.")
            logging.info(f"Custom dates parsed to these absolute values:\n"
                         f" Date From: {start_date.isoformat(timespec='seconds')},"
                         f" Date To: {end_date.isoformat(timespec='seconds')}")
            time.CustomDateRangeStart.Year = start_date.year
            time.CustomDateRangeStart.Month = start_date.month
            time.CustomDateRangeStart.Day = start_date.day
            time.CustomDateRangeEnd.Year = end_date.year
            time.CustomDateRangeEnd.Month = end_date.month
            time.CustomDateRangeEnd.Day = end_date.day
        else:
            time.PredefinedTime = period
            time.CustomDateRangeStart = None
            time.CustomDateRangeEnd = None

    def _set_report_request_columns_parameter_and_primary_key(self):
        report_columns = self._report_request.Columns
        column_array: list[str] = getattr(report_columns, self._report_type + "ReportColumn")
        column_spec = self.config_dict.get(KEY_COLUMNS) or self.config_dict.get(KEY_COLUMNS_ARRAY, [])
        if isinstance(column_spec, str):
            column_names = comma_separated_str_to_list(column_spec)
        elif isinstance(column_spec, list):
            column_names = column_spec
        column_array.extend(column_names)
        primary_key_spec = self.config_dict.get(KEY_PRIMARY_KEY) or self.config_dict.get(KEY_PRIMARY_KEY_ARRAY, [])
        if isinstance(primary_key_spec, str):
            self.primary_key = comma_separated_str_to_list(primary_key_spec)
        elif isinstance(primary_key_spec, list):
            self.primary_key = primary_key_spec
        primary_key_columns_not_in_columns = set(self.primary_key) - set(column_names)
        if primary_key_columns_not_in_columns:
            raise UserException(
                f"Some primary key columns are not in columns: {', '.join(primary_key_columns_not_in_columns)}."
                f" Primary key columns must be a subset of columns.")

    def _set_report_request_scope_parameter(self):
        self._report_request.Scope.AccountIds = {"long": [self._authorization_data.account_id]}
