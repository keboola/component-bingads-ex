from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from suds import WebFault

from bingads.v13.bulk import BulkServiceManager
from bingads.v13.bulk import DownloadParameters as BulkDownloadParameters
from bingads.v13.reporting import ReportingServiceManager, ReportingDownloadParameters

from .authorization import Authorization
from .bulk import create_download_parameters as create_bulk_download_parameters
from .error_handling import output_webfault_errors

# from .reporting import ReportingDownloadClient

KEY_TYPE = "type"
REPORT_FILE_FORMAT = "Csv"


@dataclass(slots=True)
class DownloadRequest:
    authorization: Authorization
    config_dict: dict
    result_file_directory: str
    result_file_name: str
    last_sync_time_in_utc: datetime | None = None

    _download_parameters: BulkDownloadParameters | ReportingDownloadParameters = field(
        init=False
    )
    _service_manager: BulkServiceManager | ReportingServiceManager = field(init=False)

    def __post_init__(self):
        _type: Literal["Bulk", "Reporting"] = self.config_dict[KEY_TYPE]
        if _type == "Bulk":
            self._service_manager = BulkServiceManager(
                authorization_data=self.authorization.authorization_data,
                environment=self.authorization.environment,
            )
            self._download_parameters = create_bulk_download_parameters(
                config_dict=self.config_dict,
                last_sync_time_in_utc=self.last_sync_time_in_utc,
                result_file_directory=self.result_file_directory,
                result_file_name=self.result_file_name,
            )
        elif _type == "Reporting":
            raise NotImplementedError("Reporting is not implemented yet.")
        else:
            raise ValueError(f"Unsupported type: {_type}")

    def process(self):
        try:
            self._service_manager.download_file(self._download_parameters)
        except WebFault as ex:
            output_webfault_errors(ex)
            raise
