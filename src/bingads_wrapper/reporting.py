from dataclasses import dataclass
import logging
import time

from suds import WebFault

from bingads.service_client import ServiceClient
from bingads.v13.reporting import (
    ReportingServiceManager,
    ReportingDownloadParameters,
    ReportingDownloadOperation,
)


from .authorization import Authorization
from .error_handling import output_webfault_errors


@dataclass(slots=True)
class BingAdsPerformanceReport:
    authorization: Authorization

    def get_campaign_performance_report_request(self):
        reporting_service = ServiceClient(
            service="ReportingService",
            version=13,
            authorization_data=self.authorization.authorization_data,
        )
        account_id = self.authorization.account_id
        report_request = reporting_service.factory.create(
            "CampaignPerformanceReportRequest"
        )
        report_request.Time = time
        report_request.ReportName = "Test performance report"
        scope = reporting_service.factory.create("AccountThroughCampaignReportScope")
        scope.AccountIds = {"long": [account_id]}
        scope.Campaigns = None
        report_request.Scope = scope

        report_columns = reporting_service.factory.create(
            "ArrayOfCampaignPerformanceReportColumn"
        )
        # report_columns.CampaignPerformanceReportColumn.append([
        # 'null',
        # 'array'
        # ])
        report_request.Columns = report_columns

        return report_request

    def submit_and_download(self, report_request, directory, filename):
        """Submit the download request and then use the ReportingDownloadOperation result to
        track status until the report is complete e.g. either using
        ReportingDownloadOperation.track() or ReportingDownloadOperation.get_status()."""

        try:
            reporting_service_manager = ReportingServiceManager(
                self.authorization.authorization_data,
                environment=self.authorization.environment,
            )
            reporting_download_operation = reporting_service_manager.submit_download(
                report_request
            )

            reporting_operation_status = reporting_download_operation.track(
                timeout_in_milliseconds=20000
            )
            result_file_path = reporting_download_operation.download_result_file(
                result_file_directory=directory,
                result_file_name=filename,
                decompress=True,
                overwrite=True,  # Set this value true if you want to overwrite the same file.
                timeout_in_milliseconds=1000
                # You may optionally cancel the download after a specified time interval.
            )

        except WebFault as ex:
            output_webfault_errors(ex)
            raise

        return result_file_path

    # def performance_report_download(
    #     self, directory: str
    # ):
    #     reporting_service_manager = ReportingServiceManager(
    #         authorization_data=self.authorization.authorization_data,
    #         environment=self.authorization.environment
    #     )
    #     submit_download_parameters_for_reporting_file = ReportingDownloadParameters(
    #         report_request = self.report_request,
    #         result_file_directory= directory,
    #         result_file_name= "reporting_test_file.csv",
    #         decompress_result_file= True,
    #     )
    #     try:
    #         reporting_download_operation = reporting_service_manager.submit_download(
    #             submit_download_parameters_for_reporting_file
    #         )
    #     except WebFault as ex:
    #         output_webfault_errors(ex)
    #
    #     return reporting_download_operation
