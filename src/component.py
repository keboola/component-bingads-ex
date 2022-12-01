from datetime import datetime, timezone
from enum import Enum, unique
import logging
import os
from typing import Optional
from pathlib import Path
import json
import jsonschema

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

from bingads_wrapper.authorization import Authorization

from bingads_wrapper.request import DownloadRequest, ReportDownloadRequest, BulkDownloadRequest

# Global configuration variables
KEY_AUTHORIZATION = "authorization"

# Row configuration variables
KEY_OBJECT_TYPE = "object_type"
KEY_DESTINATION = "destination"
KEY_BULK_SETTINGS = "bulk_settings"
KEY_REPORT_SETTINGS_CUSTOM = "report_settings_custom"
KEY_REPORT_SETTINGS_PREBUILT = "report_settings_prebuilt"

# Destination variables
KEY_OUTPUT_TABLE_NAME = "output_table_name"
KEY_LOAD_TYPE = "load_type"

# list of mandatory parameters => if some is missing,
# component will fail with readable message on initialization.
REQUIRED_PARAMETERS = (KEY_AUTHORIZATION, KEY_OBJECT_TYPE, KEY_DESTINATION)
REQUIRED_IMAGE_PARAMETERS = ()

# State variables
KEY_REFRESH_TOKEN = "#refresh_token"
KEY_NONCE = "#nonce"
KEY_LAST_SYNC_TIME_IN_UTC = "last_sync_time_in_utc"

# Other constants
NONCE_LENGTH = 32


# Row config enums:
@unique
class ObjectType(Enum):
    """
    object_type row config parameter enum
    """
    ENTITY = "entity"
    REPORT_PREBUILT = "report_prebuilt"
    REPORT_CUSTOM = "report_custom"


@unique
class LoadType(Enum):
    FULL = "full_load"
    INCREMENTAL = "incremental_load"


def get_schema():
    """
    Returns JSON schema for the component configuration.
    """
    component_config_dir = Path(__file__).parent.parent / "component_config"
    schema_path = component_config_dir / "configSchema.json"
    row_schema_path = component_config_dir / "configRowSchema.json"
    with open(schema_path, "r") as schema_file:
        schema = json.load(schema_file)
    with open(row_schema_path, "r") as row_schema_file:
        row_schema = json.load(row_schema_file)
    row_schema["required"] = schema["required"] + row_schema["required"]
    row_schema["properties"] = schema["properties"] | row_schema["properties"]
    return row_schema


class BingAdsExtractor(ComponentBase):
    """
    Extends base class for general Python components. Initializes the CommonInterface
    and performs configuration validation.

    For easier debugging the data folder is picked up by default from `../data` path,
    relative to working directory.

    If `debug` parameter is present in the `config.json`, the default logger is set to verbose DEBUG mode.
    """
    def __init__(self, data_path_override: Optional[str] = None):
        super().__init__(data_path_override)
        self.validate_configuration_parameters(REQUIRED_PARAMETERS)
        self.validate_image_parameters(REQUIRED_IMAGE_PARAMETERS)
        os.makedirs(self.tables_out_path, exist_ok=True)
        params: dict = self.configuration.parameters
        if params.get("debug"):
            try:
                jsonschema.validate(params, get_schema())
            except jsonschema.ValidationError as e:
                raise UserException(f"Configuration validation error: {e.message}."
                                    f" Please make sure provided configuration is valid.") from e
        self.previous_state = self.get_state_file()
        last_sync_time_in_utc_str: Optional[str] = self.previous_state.get(KEY_LAST_SYNC_TIME_IN_UTC)
        self.last_sync_time_in_utc = (datetime.fromisoformat(last_sync_time_in_utc_str)
                                      if last_sync_time_in_utc_str else None)
        self.sync_time_in_utc_str = last_sync_time_in_utc_str  # Saving the old timestamp until new sync is done

    def run(self):
        """
        Main execution code
        """
        params: dict = self.configuration.parameters
        if params.get("debug"):
            try:
                jsonschema.validate(params, get_schema())
            except jsonschema.ValidationError as e:
                raise UserException(f"Configuration validation error: {e.message}."
                                    f" Please make sure provided configuration is valid.") from e

        authorization_dict = params[KEY_AUTHORIZATION]
        object_type = ObjectType(params[KEY_OBJECT_TYPE])
        destination: dict = params[KEY_DESTINATION]
        incremental: bool = LoadType(destination[KEY_LOAD_TYPE]) is LoadType.INCREMENTAL
        table_name: str = destination[KEY_OUTPUT_TABLE_NAME]

        refresh_token_from_state: str = self.previous_state.get(KEY_REFRESH_TOKEN)

        authorization = Authorization(config_dict=authorization_dict,
                                      oauth_credentials=self.get_oauth_credentials(),
                                      save_refresh_token_function=self.save_state,
                                      refresh_token_from_state=refresh_token_from_state)

        if object_type is ObjectType.ENTITY:
            download_request_config_dict: dict = params[KEY_BULK_SETTINGS]
            download_request_class = BulkDownloadRequest
        elif object_type in (ObjectType.REPORT_CUSTOM, ObjectType.REPORT_PREBUILT):
            download_request_config_dict: dict = (params[KEY_REPORT_SETTINGS_CUSTOM]
                                                  if object_type is ObjectType.REPORT_CUSTOM else
                                                  params[KEY_REPORT_SETTINGS_PREBUILT])
            download_request_class = ReportDownloadRequest
        else:
            raise RuntimeError("Unexpected execution branch.")
        download_request: DownloadRequest = download_request_class(
            authorization=authorization,
            config_dict=download_request_config_dict,
            result_file_directory=self.tables_out_path,
            table_name=table_name,
            last_sync_time_in_utc=self.last_sync_time_in_utc,
        )
        new_sync_time_in_utc_str = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
        download_request.process()

        table_def = self.create_out_table_definition(download_request.result_file_name, incremental=incremental)
        table_def.primary_key = download_request.primary_key

        if os.path.exists(table_def.full_path):  # Checking whether a CSV file was created
            self.write_manifest(table_def)

        self.sync_time_in_utc_str = new_sync_time_in_utc_str  # Extraction done, updating sync timestamp in state
        self.save_state(authorization.refresh_token)

    def save_state(self, refresh_token: str):
        """
        Save refresh token to state file.
        """
        self.write_state_file({
            KEY_REFRESH_TOKEN: refresh_token,
            KEY_LAST_SYNC_TIME_IN_UTC: self.sync_time_in_utc_str,
        })

    def get_oauth_credentials(self) -> dict:
        return self.configuration.oauth_credentials


"""
        Main entrypoint
"""
if __name__ == "__main__":
    try:
        comp = BingAdsExtractor()
        # this triggers the run method by default and is controlled by the configuration.action parameter
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
