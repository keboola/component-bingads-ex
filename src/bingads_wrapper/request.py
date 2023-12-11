from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from bingads.v13.bulk import BulkServiceManager
from bingads.v13.bulk import DownloadParameters as BulkDownloadParameters
from bingads.v13.reporting import ReportingServiceManager, ReportingDownloadParameters
from suds import WebFault

from .authorization import Authorization
from .bulk import create_download_parameters as create_bulk_download_parameters
from .bulk import create_primary_key as create_bulk_primary_key
from .error_handling import process_webfault_errors
from .reporting import ReportingDownloadParametersFactory

import backoff
import urllib.error

REPORT_FILE_FORMAT = "Csv"


@dataclass(slots=True)
class DownloadRequest(ABC):
    authorization: Authorization
    config_dict: dict
    result_file_directory: str
    table_name: Optional[str] = None
    last_sync_time_in_utc: Optional[datetime] = None

    primary_key: list[str] = field(init=False)
    result_file_name: str = field(init=False)

    _download_parameters: BulkDownloadParameters | ReportingDownloadParameters = field(init=False)
    _service_manager: BulkServiceManager | ReportingServiceManager = field(init=False)

    @abstractmethod
    def __post_init__(self):
        pass  # Initialization of uninitialized/optional fields must be done in derived classes

    @backoff.on_exception(backoff.expo, (ConnectionError, urllib.error.URLError), max_tries=5)
    def process(self):
        try:
            self._service_manager.download_file(self._download_parameters)
        except WebFault as ex:
            process_webfault_errors(ex)


class BulkDownloadRequest(DownloadRequest):
    def __post_init__(self):
        if not self.table_name:
            self.table_name = "Entities"
        self.result_file_name = f"{self.table_name}.csv"
        self._service_manager = BulkServiceManager(
            authorization_data=self.authorization.authorization_data,
            environment=self.authorization.environment,
        )
        self._download_parameters = create_bulk_download_parameters(
            config_dict=self.config_dict,
            last_sync_time_in_utc=self.last_sync_time_in_utc,
            result_file_directory=self.result_file_directory,
            result_file_name=self.result_file_name,
            report_file_format=REPORT_FILE_FORMAT,
        )
        self.primary_key = create_bulk_primary_key()


class ReportDownloadRequest(DownloadRequest):
    def __post_init__(self):
        if self.table_name:
            self.result_file_name = f"{self.table_name}.csv"
        else:
            self.result_file_name = None
        self._service_manager = ReportingServiceManager(
            authorization_data=self.authorization.authorization_data,
            environment=self.authorization.environment,
        )
        reporting_download_parameters_factory = ReportingDownloadParametersFactory(
            config_dict=self.config_dict,
            result_file_directory=self.result_file_directory,
            result_file_name=self.result_file_name,
            report_file_format=REPORT_FILE_FORMAT,
            reporting_service=self._service_manager._service_client,
            last_sync_time_in_utc=self.last_sync_time_in_utc)
        self._download_parameters = reporting_download_parameters_factory.create()
        if not self.table_name:
            self.result_file_name = reporting_download_parameters_factory.result_file_name
            self.table_name = self.result_file_name.removesuffix(".csv")
        self.primary_key = reporting_download_parameters_factory.primary_key
