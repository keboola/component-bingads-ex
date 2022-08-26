from dataclasses import dataclass, field

from datetime import datetime
from typing import List

from suds import WebFault

from bingads.service_client import ServiceClient
from bingads.v13.bulk import (
    BulkServiceManager,
    SubmitDownloadParameters,
    BulkDownloadOperation,
    BulkOperationStatus,
)

from keboola.component.exceptions import UserException

from .authorization import Authorization
from .error_handling import output_webfault_errors

KEY_DATA_SCOPE = "data_scope"
KEY_DOWNLOAD_ENTITIES = "download_entities"

DOWNLOAD_REQUEST_TIMEOUT_PERIOD_MILLISECONDS = 60 * 1000
REPORT_FILE_FORMAT = "Csv"


@dataclass(slots=True)
class BulkDownloadsClient:
    authorization: Authorization
    _bulk_service: ServiceClient = field(init=False)
    _bulk_service_manager: BulkServiceManager = field(init=False)

    def __post_init__(self):
        self._bulk_service_manager = BulkServiceManager(
            authorization_data=self.authorization.authorization_data,
            environment=self.authorization.environment,
        )
        self._bulk_service = self._bulk_service_manager._service_client

    def submit_download(
        self, submit_download_parameters: SubmitDownloadParameters
    ) -> BulkDownloadOperation:
        try:
            bulk_download_operation = self._bulk_service_manager.submit_download(
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


@dataclass(slots=True)
class BulkDownload:
    client: BulkDownloadsClient
    config_dict: dict
    result_file_directory_path: str
    result_filename: str
    last_sync_time_in_utc: datetime | None = None

    _submit_parameters: SubmitDownloadParameters = field(init=False)
    _operation: BulkDownloadOperation | None = field(init=False, default=None)
    _status: BulkOperationStatus | None = field(init=False, default=None)
    downloaded: bool = field(init=False, default=False)

    def __post_init__(self):
        data_scope: List[str] = self.config_dict[KEY_DATA_SCOPE]
        download_entities: List[str] = self.config_dict[KEY_DOWNLOAD_ENTITIES]
        self._submit_parameters = SubmitDownloadParameters(
            campaign_ids=None,
            data_scope=data_scope,
            download_entities=download_entities,
            file_type=REPORT_FILE_FORMAT,
            last_sync_time_in_utc=self.last_sync_time_in_utc,
        )

    def submit(self) -> None:
        self._operation = self.client.submit_download(self._submit_parameters)

    def update_status(self) -> None:
        self._status = self.client.get_download_status(self._operation)
        if self._status.status == "Failed":
            raise UserException(
                "Download request failed."
                " You may submit a new download with fewer entities, without quality score and bid suggestions data,"
                " or try again to submit the same download later."
            )
        elif self._status.status == "FailedFullSyncRequired":
            raise UserException("Download request failed. Full sync required.")

    def download_file(self) -> None:
        self.client.download_file(
            self._operation, self.result_file_directory_path, self.result_filename
        )
        self.downloaded = True

    def process(self):
        if self._operation is None:
            self.submit()
            return
        if self._status is None or self._status.status == "InProgress":
            self.update_status()
        if self._status._status == "Completed" and not self.downloaded:
            self.download_file()
            return
        if self._status.status == "InProgress" or self.downloaded:
            return
        raise Exception("Unexpected state encountered.")
