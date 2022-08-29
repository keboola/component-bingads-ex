from datetime import datetime
from typing import List

from bingads.v13.bulk import DownloadParameters

KEY_DATA_SCOPE = "data_scope"
KEY_DOWNLOAD_ENTITIES = "download_entities"
KEY_SINCE_LAST_SYNC_TIME = "since_last_sync_time"

DOWNLOAD_REQUEST_TIMEOUT_PERIOD_MILLISECONDS = 60 * 1000
OVERWRITE_RESULT_FILE = True


def create_download_parameters(
    config_dict: dict,
    last_sync_time_in_utc: datetime | None,
    result_file_directory: str,
    result_file_name: str,
    report_file_format: str,
) -> DownloadParameters:
    data_scope: List[str] = config_dict[KEY_DATA_SCOPE]
    download_entities: List[str] = config_dict[KEY_DOWNLOAD_ENTITIES]
    since_last_sync_time: bool = config_dict.get(KEY_SINCE_LAST_SYNC_TIME, False)
    _last_sync_time_in_utc = last_sync_time_in_utc if since_last_sync_time else None
    return DownloadParameters(
        campaign_ids=None,
        data_scope=data_scope,
        download_entities=download_entities,
        file_type=report_file_format,
        last_sync_time_in_utc=_last_sync_time_in_utc,
        result_file_directory=result_file_directory,
        result_file_name=result_file_name,
        overwrite_result_file=OVERWRITE_RESULT_FILE,
        timeout_in_milliseconds=DOWNLOAD_REQUEST_TIMEOUT_PERIOD_MILLISECONDS,
    )
