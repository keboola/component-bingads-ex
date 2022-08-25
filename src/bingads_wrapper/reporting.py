from dataclasses import dataclass, field

from suds import WebFault

from bingads.service_client import ServiceClient
from bingads.v13.reporting import (
    ReportingServiceManager,
    ReportingDownloadOperation,
)


from .authorization import Authorization
from .error_handling import output_webfault_errors

REPORT_FILE_FORMAT = "Csv"


@dataclass(slots=True)
class ReportingDownloadClient:
    authorization: Authorization
    _reporting_service: ServiceClient = field(init=False)
    _reporting_service_manager: ReportingServiceManager = field(init=False)

    def __post_init__(self):
        self._reporting_service_manager = ReportingServiceManager(
            authorization_data=self.authorization.authorization_data,
            environment=self.authorization.environment,
        )
        self._reporting_service = self._reporting_service_manager._service_client

    def create_campaign_performance_report_request(self):
        aggregation = "Daily"
        exclude_column_headers = False
        exclude_report_footer = True
        exclude_report_header = True
        time = self._reporting_service.factory.create("ReportTime")
        # You can either use a custom date range or predefined time.
        time.PredefinedTime = None  # "Yesterday"
        time.ReportTimeZone = None  # "PacificTimeUSCanadaTijuana"
        time.CustomDateRangeStart = self._reporting_service.factory.create("Date")
        time.CustomDateRangeStart.Year = 2022
        time.CustomDateRangeStart.Month = 8
        time.CustomDateRangeStart.Day = 1
        time.CustomDateRangeEnd = self._reporting_service.factory.create("Date")
        time.CustomDateRangeEnd.Year = 2022
        time.CustomDateRangeEnd.Month = 8
        time.CustomDateRangeEnd.Day = 25
        return_only_complete_data = False

        report_request = self._reporting_service.factory.create(
            "CampaignPerformanceReportRequest"
        )
        report_request.Aggregation = aggregation
        report_request.ExcludeColumnHeaders = exclude_column_headers
        report_request.ExcludeReportFooter = exclude_report_footer
        report_request.ExcludeReportHeader = exclude_report_header
        report_request.Format = REPORT_FILE_FORMAT
        report_request.ReturnOnlyCompleteData = return_only_complete_data
        report_request.Time = time
        report_request.ReportName = "My Campaign Performance Report"
        scope = self._reporting_service.factory.create(
            "AccountThroughCampaignReportScope"
        )
        scope.AccountIds = {"long": [self.authorization.account_id]}
        scope.Campaigns = None
        report_request.Scope = scope

        report_columns = self._reporting_service.factory.create(
            "ArrayOfCampaignPerformanceReportColumn"
        )
        report_columns.CampaignPerformanceReportColumn.append(
            [
                "TimePeriod",
                "CampaignId",
                "CampaignName",
                "DeviceType",
                "Network",
                "Impressions",
                "Clicks",
                "Spend",
            ]
        )
        report_request.Columns = report_columns

        return report_request

    def submit_download(self, report_request) -> ReportingDownloadOperation:
        try:
            reporting_download_operation = (
                self._reporting_service_manager.submit_download(report_request)
            )
        except WebFault as ex:
            output_webfault_errors(ex)
            raise

        return reporting_download_operation
