from dataclasses import dataclass
import time
from typing import List

from suds import WebFault

from bingads.v13.bulk import (
    BulkServiceManager,
    SubmitDownloadParameters,
    BulkDownloadOperation,
    BulkOperationStatus,
)


from .authorization import Authorization
from .error_handling import output_webfault_errors

DOWNLOAD_REQUEST_TIMEOUT_PERIOD_MILLISECONDS = 60 * 1000


@dataclass(slots=True, frozen=True)
class DownloadRequestSpec:
    data_scope: List[str]
    download_entities: List[str]


@dataclass(slots=True)
class BulkDownloadsClient:
    authorization: Authorization

    def submit_download(
        self, data_scope: List[str], download_entities: List[str]
    ) -> BulkDownloadOperation:
        bulk_service_manager = BulkServiceManager(
            authorization_data=self.authorization.authorization_data,
            environment=self.authorization.environment,
        )
        submit_download_parameters = SubmitDownloadParameters(
            campaign_ids=None,
            data_scope=data_scope,
            download_entities=download_entities,
            file_type="Csv",
            last_sync_time_in_utc=None,
        )
        try:
            bulk_download_operation = bulk_service_manager.submit_download(
                submit_download_parameters
            )
        except WebFault as ex:
            output_webfault_errors(ex)
            raise

        return bulk_download_operation

    def get_download_status(
        self, bulk_download_operation: BulkDownloadOperation
    ) -> BulkOperationStatus:
        try:
            bulk_operation_status = bulk_download_operation.get_status()
        except WebFault as ex:
            output_webfault_errors(ex)
            raise

        return bulk_operation_status

    def download_file(
        self,
        bulk_download_operation: BulkDownloadOperation,
        directory: str,
        filename: str,
    ) -> str:
        try:
            filepath = bulk_download_operation.download_result_file(
                result_file_directory=directory,
                result_file_name=filename,
                decompress=True,
                overwrite=True,
                timeout_in_milliseconds=DOWNLOAD_REQUEST_TIMEOUT_PERIOD_MILLISECONDS,
            )
        except WebFault as ex:
            output_webfault_errors(ex)
            raise

        return filepath

    def perform_all_download_operations(
        self,
        bulk_download_operation_specs: List[DownloadRequestSpec],
        download_directory: str,
        filename_prefix: str,
    ):
        """
        Perform all download operations.
        """
        bulk_download_operations = [
            self.submit_download(
                data_scope=spec.data_scope, download_entities=spec.download_entities
            )
            for spec in bulk_download_operation_specs
        ]
        all_done = False
        bulk_download_operations_to_be_completed = bulk_download_operations.copy()
        bulk_download_operations_to_be_removed: List[BulkDownloadOperation] = []
        completed_downloads = 0
        while not all_done:
            all_done = True
            time.sleep(1)
            for bulk_download_operation in bulk_download_operations_to_be_removed:
                bulk_download_operations_to_be_completed.remove(bulk_download_operation)
            bulk_download_operations_to_be_removed.clear()
            for bulk_download_operation in bulk_download_operations_to_be_completed:
                bulk_operation_status = self.get_download_status(
                    bulk_download_operation
                )
                if bulk_operation_status.status == "InProgress":
                    all_done = False
                elif bulk_operation_status.status == "Failed":
                    raise Exception(
                        "Download operation failed with status: {0}".format(
                            bulk_operation_status.status
                        )
                    )
                elif bulk_operation_status.status == "Completed":
                    self.download_file(
                        bulk_download_operation=bulk_download_operation,
                        directory=download_directory,
                        filename=filename_prefix + str(completed_downloads) + ".csv",
                    )
                    completed_downloads += 1
                    bulk_download_operations_to_be_removed.append(
                        bulk_download_operation
                    )
                else:
                    raise Exception(
                        "Download operation failed with status: {0}".format(
                            bulk_operation_status.status
                        )
                    )
