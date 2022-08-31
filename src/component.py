"""
Template Component main class.

"""
from datetime import datetime, timezone
import logging
import os
import secrets
import string
from typing import Optional
from pathlib import Path
import json
import jsonschema

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

from bingads_wrapper.authorization import (
    Authorization,
)

from bingads_wrapper.request import DownloadRequest

# configuration variables
KEY_AUTHORIZATION = "authorization"
KEY_DOWNLOAD_REQUEST = "download_request"
KEY_TABLE_NAME = "table_name"
KEY_LOAD_MODE = "load_mode"

# list of mandatory parameters => if some is missing,
# component will fail with readable message on initialization.
REQUIRED_PARAMETERS = [
    KEY_AUTHORIZATION,
    KEY_TABLE_NAME,
    KEY_LOAD_MODE,
    KEY_DOWNLOAD_REQUEST,
]
REQUIRED_IMAGE_PARS = []

# State variables
KEY_REFRESH_TOKEN = "#refresh_token"
KEY_NONCE = "#nonce"
KEY_LAST_SYNC_TIME_IN_UTC = "last_sync_time_in_utc"

# Other constants
NONCE_LENGTH = 32


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

    def run(self):
        """
        Main execution code
        """
        self.validate_configuration_parameters(REQUIRED_PARAMETERS)
        self.validate_image_parameters(REQUIRED_IMAGE_PARS)
        os.makedirs(self.tables_out_path, exist_ok=True)

        params: dict = self.configuration.parameters
        if params.get("debug"):
            try:
                jsonschema.validate(params, get_schema())
            except jsonschema.ValidationError as e:
                raise UserException(
                    f"Configuration validation error: {e.message}."
                    f" Please make sure provided configuration is valid."
                ) from e

        authorization_dict = params[KEY_AUTHORIZATION]
        table_name: str = params[KEY_TABLE_NAME]
        incremental: bool = params[KEY_LOAD_MODE] == "Incremental"
        download_request_dict: dict = params[KEY_DOWNLOAD_REQUEST]

        # get last state data/in/state.json from previous run
        previous_state = self.get_state_file()
        refresh_token: Optional[str] = previous_state.get(KEY_REFRESH_TOKEN)
        self.nonce: str = previous_state.get(
            KEY_NONCE,
            "".join(
                secrets.choice(string.ascii_letters + string.digits)
                for _ in range(NONCE_LENGTH)
            ),
        )
        last_sync_time_in_utc_str: str | None = previous_state.get(
            KEY_LAST_SYNC_TIME_IN_UTC
        )
        last_sync_time_in_utc = (
            datetime.fromisoformat(last_sync_time_in_utc_str)
            if last_sync_time_in_utc_str
            else None
        )
        self.sync_time_in_utc_str = datetime.now(tz=timezone.utc).isoformat(
            timespec="seconds"
        )

        authorization = Authorization(
            config_dict=authorization_dict,
            refresh_token=refresh_token,
            nonce=self.nonce,
            save_refresh_token_function=self.save_state,
        )

        table_def = self.create_out_table_definition(
            f"{table_name}.csv", incremental=incremental
        )

        download_request = DownloadRequest(
            authorization=authorization,
            config_dict=download_request_dict,
            result_file_directory=self.tables_out_path,
            result_file_name=table_def.name,
            last_sync_time_in_utc=last_sync_time_in_utc,
        )
        download_request.process()

        table_def.primary_key = download_request.primary_key

        self.write_manifest(table_def)

        self.save_state(authorization.refresh_token)

    def save_state(self, refresh_token: str):
        """
        Save refresh token and nonce to state file.
        """
        self.write_state_file(
            {
                KEY_REFRESH_TOKEN: refresh_token,
                KEY_NONCE: self.nonce,
                KEY_LAST_SYNC_TIME_IN_UTC: self.sync_time_in_utc_str,
            }
        )


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
