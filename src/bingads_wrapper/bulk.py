from datetime import datetime, timedelta, timezone
import logging
from typing import List, Optional

from bingads.v13.bulk import DownloadParameters

from .utils import comma_separated_str_to_list

KEY_DATA_SCOPE = "data_scope"
KEY_DOWNLOAD_ENTITIES = "download_entities"
KEY_SINCE_LAST_SYNC_TIME = "since_last_sync_time"

DOWNLOAD_REQUEST_TIMEOUT_PERIOD_MILLISECONDS = 60 * 1000
OVERWRITE_RESULT_FILE = True
DEFAULT_DATA_SCOPE = ["EntityData"]
DATA_SCOPES_INCOMPATIBLE_WITH_LAST_SYNC_TIME = {"QualityScoreData", "BidSuggestionsData"}


def _get_last_sync_time_argument(config_dict: dict, data_scope: List[str],
                                 last_sync_time_in_utc: Optional[datetime]) -> Optional[datetime]:
    since_last_sync_time: bool = config_dict.get(KEY_SINCE_LAST_SYNC_TIME, False)
    if not since_last_sync_time:
        return None
    elif not last_sync_time_in_utc:
        logging.warning(
            '"Only download changes since the last run" option is used, but no last run timestamp was found'
            ' (probably caused by this being the first run of this configuration row). Will download all data.')
        return None
    incompatible_data_scope_elements = DATA_SCOPES_INCOMPATIBLE_WITH_LAST_SYNC_TIME.intersection(data_scope)
    if incompatible_data_scope_elements:
        logging.warning(f"Data scope elements {incompatible_data_scope_elements} are incompatible with"
                        f" only downloading changes since the last run. Will download all data.")
        return None
    last_sync_time_to_now: timedelta = datetime.now(tz=timezone.utc) - last_sync_time_in_utc
    if last_sync_time_to_now.days >= 30:
        logging.warning("Last sync done more than 30 days ago, cannot do incremental sync. Will download all data.")
        return None
    return last_sync_time_in_utc


def create_download_parameters(
    config_dict: dict,
    last_sync_time_in_utc: Optional[datetime],
    result_file_directory: str,
    result_file_name: str,
    report_file_format: str,
) -> DownloadParameters:
    data_scope: List[str] = (comma_separated_str_to_list(config_dict[KEY_DATA_SCOPE])
                             if config_dict.get(KEY_DATA_SCOPE) else DEFAULT_DATA_SCOPE)
    download_entities: List[str] = comma_separated_str_to_list(config_dict[KEY_DOWNLOAD_ENTITIES])
    return DownloadParameters(
        campaign_ids=None,
        data_scope=data_scope,
        download_entities=download_entities,
        file_type=report_file_format,
        last_sync_time_in_utc=_get_last_sync_time_argument(config_dict, data_scope, last_sync_time_in_utc),
        result_file_directory=result_file_directory,
        result_file_name=result_file_name,
        overwrite_result_file=OVERWRITE_RESULT_FILE,
        timeout_in_milliseconds=DOWNLOAD_REQUEST_TIMEOUT_PERIOD_MILLISECONDS,
    )


def create_primary_key() -> List[str]:
    return ["Type", "Id"]
