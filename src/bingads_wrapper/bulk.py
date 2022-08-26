from datetime import datetime
from typing import List

from bingads.v13.bulk import DownloadParameters

KEY_DATA_SCOPE = "data_scope"
KEY_DOWNLOAD_ENTITIES = "download_entities"

DOWNLOAD_REQUEST_TIMEOUT_PERIOD_MILLISECONDS = 60 * 1000
REPORT_FILE_FORMAT = "Csv"


def create_download_parameters(
    config_dict: dict,
    last_sync_time_in_utc: datetime | None,
    result_file_directory: str,
    result_file_name: str,
) -> DownloadParameters:
    data_scope: List[str] = config_dict[KEY_DATA_SCOPE]
    download_entities: List[str] = config_dict[KEY_DOWNLOAD_ENTITIES]
    return DownloadParameters(
        campaign_ids=None,
        data_scope=data_scope,
        download_entities=download_entities,
        file_type=REPORT_FILE_FORMAT,
        last_sync_time_in_utc=last_sync_time_in_utc,
        result_file_directory=result_file_directory,
        result_file_name=result_file_name,
        overwrite_result_file=True,
        timeout_in_milliseconds=DOWNLOAD_REQUEST_TIMEOUT_PERIOD_MILLISECONDS,
    )
