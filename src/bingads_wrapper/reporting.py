import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from bingads.authorization import AuthorizationData
from bingads.v13.reporting import ReportingDownloadParameters
from dateparser import parse
from keboola.component.exceptions import UserException
from pydantic import BaseModel

from .prebuilt_configs import get_prebuilt_report_config
from .rest_compat import build_nested, create_report_request, declares_field, set_field
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

MAX_COMPONENT_RUNTIME_SECONDS = 14400
DOWNLOAD_REQUEST_TIMEOUT_PERIOD_MILLISECONDS = (MAX_COMPONENT_RUNTIME_SECONDS - 400) * 1000
OVERWRITE_RESULT_FILE = True

EXCLUDE_COLUMNS_HEADERS = False
EXCLUDE_REPORT_FOOTER = True
EXCLUDE_REPORT_HEADER = True
DEFAULT_FORMAT_VERSION = "2.0"

# this is only because ProductDimensionPerformance does not allow AccountId only AccountNumber
# https://learn.microsoft.com/en-us/advertising/reporting-service/productdimensionperformancereportcolumn?view=bingads-13
KEY_ACCOUNT_ID_COLUMNS = ["AccountId", "AccountNumber"]


def get_account_column(report_type: str):
    """
    this is only because ProductDimensionPerformance does not allow AccountId only AccountNumber
    https://learn.microsoft.com/en-us/advertising/reporting-service/productdimensionperformancereportcolumn
    ?view=bingads-13
    """
    if report_type == 'ProductDimensionPerformance':
        return "AccountNumber"
    else:
        return "AccountId"


@dataclass(slots=True)
class ReportingDownloadParametersFactory:
    authorization_data: AuthorizationData
    config_dict: dict[str, str | list[str]]
    result_file_directory: str
    report_file_format: str

    result_file_name: Optional[str] = None
    last_sync_time_in_utc: Optional[datetime] = None

    primary_key: list[str] = field(init=False)

    _authorization_data: AuthorizationData = field(init=False)
    _report_type: str = field(init=False)
    _report_request: BaseModel = field(init=False)

    def __post_init__(self):
        self._authorization_data = self.authorization_data
        config_keys = set(self.config_dict.keys())
        missing_config_dict_keys = {
                                       KEY_REPORT_TYPE, KEY_COLUMNS_ARRAY, KEY_PRIMARY_KEY_ARRAY} - config_keys

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
        self._report_request = create_report_request(self._report_type)
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
        # These guards ask whether the report type supports the element. Under SOAP that
        # was a hasattr() check on the generated object. Pydantic declares every optional
        # field on the class, so hasattr() is always true and would change the behaviour.
        # declares_field() checks the declared fields instead and keeps the original test.
        self._set_report_request_base_parameters()
        if declares_field(self._report_request, "Time"):
            self._set_report_request_time_parameter()
        if declares_field(self._report_request, "Columns"):
            self._set_report_request_columns_parameter_and_primary_key()
        if declares_field(self._report_request, "Aggregation"):
            self._set_report_request_aggregation_parameter()
        if declares_field(self._report_request, "Scope"):
            self._set_report_request_scope_parameter()

    def _set_report_request_base_parameters(self):
        self._report_request.ExcludeColumnHeaders = EXCLUDE_COLUMNS_HEADERS
        self._report_request.ExcludeReportFooter = EXCLUDE_REPORT_FOOTER
        self._report_request.ExcludeReportHeader = EXCLUDE_REPORT_HEADER
        # REST enum fields hold a plain value. The SOAP .set() method does not exist.
        set_field(self._report_request, "Format", self.report_file_format)
        self._report_request.FormatVersion = self.config_dict.get(
            KEY_FORMAT_VERSION, DEFAULT_FORMAT_VERSION)
        self._report_request.ReturnOnlyCompleteData: bool = self.config_dict[
            KEY_RETURN_ONLY_COMPLETE_DATA]

    def _set_report_request_aggregation_parameter(self):
        set_field(self._report_request, "Aggregation", self.config_dict[KEY_AGGREGATION])

    def _set_report_request_time_parameter(self):
        # SOAP created Time on first access. Pydantic leaves it as None, so it is built here.
        time_dict: dict = self.config_dict[KEY_TIME_RANGE]
        time_zone = time_dict[KEY_TIME_ZONE]
        period = time_dict[KEY_PERIOD]

        time = build_nested(self._report_request, "Time")
        set_field(time, "ReportTimeZone", time_zone)
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
            build_nested(time, "CustomDateRangeStart",
                         Year=start_date.year, Month=start_date.month, Day=start_date.day)
            build_nested(time, "CustomDateRangeEnd",
                         Year=end_date.year, Month=end_date.month, Day=end_date.day)
        else:
            set_field(time, "PredefinedTime", period)
            time.CustomDateRangeStart = None
            time.CustomDateRangeEnd = None

    def _set_report_request_columns_parameter_and_primary_key(self):
        # REST types Columns as a plain list of column names. SOAP wrapped it in an
        # ArrayOf<Type>ReportColumn element, which is why the SOAP build read that member.
        column_array: list[str] = []
        column_spec = self.config_dict.get(
            KEY_COLUMNS) or self.config_dict.get(KEY_COLUMNS_ARRAY, [])
        column_names: list[str] = []
        if isinstance(column_spec, str):
            column_names = comma_separated_str_to_list(column_spec)
        elif isinstance(column_spec, list):
            column_names = column_spec

        # column AccountId must be always present
        if not any(c in column_names for c in KEY_ACCOUNT_ID_COLUMNS):
            account_id_col = get_account_column(self._report_type)
            logging.warning(
                f"Column {account_id_col} not in columns configuration will be added!")
            column_names.append(account_id_col)
        column_array.extend(column_names)
        set_field(self._report_request, "Columns", column_array)

        primary_key_spec = self.config_dict.get(
            KEY_PRIMARY_KEY) or self.config_dict.get(KEY_PRIMARY_KEY_ARRAY, [])
        if isinstance(primary_key_spec, str):
            self.primary_key = comma_separated_str_to_list(primary_key_spec)
        elif isinstance(primary_key_spec, list):
            self.primary_key = primary_key_spec

        # column AccountId must be always present
        if not any(c in self.primary_key for c in KEY_ACCOUNT_ID_COLUMNS):
            account_id_col = get_account_column(self._report_type)
            logging.warning(
                f"Column {account_id_col} not in primary_key configuration will be added!")
            self.primary_key.append(account_id_col)

        primary_key_columns_not_in_columns = set(
            self.primary_key) - set(column_names)
        if primary_key_columns_not_in_columns:
            raise UserException(
                f"Some primary key columns are not in columns: {', '.join(primary_key_columns_not_in_columns)}."
                f" Primary key columns must be a subset of columns.")

    def _set_report_request_scope_parameter(self):
        # REST declares AccountIds as a list of strings and validates on assignment, so
        # the account id is converted. SOAP used a {"long": [...]} array wrapper here.
        build_nested(self._report_request, "Scope",
                     AccountIds=[str(self._authorization_data.account_id)])
