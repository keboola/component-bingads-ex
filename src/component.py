import json
import logging
import os
from datetime import datetime, timezone
from enum import Enum, unique
from pathlib import Path
from typing import Optional

from keboola.component.base import ComponentBase, sync_action
from keboola.component.exceptions import UserException

from bingads_wrapper import metadata_provider
from bingads_wrapper.customer_management import CustomerManagementServiceClient
from bingads_wrapper.authorization import Authorization
from bingads_wrapper.request import DownloadRequest, ReportDownloadRequest, BulkDownloadRequest

# Global configuration variables

KEY_AUTHORIZATION = "authorization"

# Row configuration variables
KEY_ACCOUNT_ID = "account_id"
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

        self.previous_state = self.get_state_file()
        last_sync_time_in_utc_str: Optional[str] = self.previous_state.get(
            KEY_LAST_SYNC_TIME_IN_UTC)
        self.last_sync_time_in_utc = (datetime.fromisoformat(last_sync_time_in_utc_str)
                                      if last_sync_time_in_utc_str else None)
        # Saving the old timestamp until new sync is done
        self.sync_time_in_utc_str = last_sync_time_in_utc_str

        self.new_sync_time_in_utc_str = datetime.now(
            tz=timezone.utc).isoformat(timespec="seconds")
        self.authorization: Authorization
        self.refresh_token_from_state: str = self.previous_state.get(
            KEY_REFRESH_TOKEN)

        # May have to be uncommented for local testing
        # try:
        #     _create_unverified_https_context = ssl._create_unverified_context
        # except AttributeError:
        #     pass
        # else:
        #     ssl._create_default_https_context = _create_unverified_https_context

    def _init_configuration(self):
        self.validate_configuration_parameters(REQUIRED_PARAMETERS)
        self._validate_configuration()

    def _init_authorization(self, account_id=None):
        authorization_dict = self.configuration.parameters[KEY_AUTHORIZATION]
        authorization_dict['#developer_token'] = authorization_dict.get(
            '#developer_token') or self.configuration.image_parameters.get('developer_token')
        try:
            self.authorization = Authorization(config_dict=authorization_dict,
                                               oauth_credentials=self.get_oauth_credentials(),
                                               save_refresh_token_function=self.save_state,
                                               refresh_token_from_state=self.refresh_token_from_state,
                                               account_id=account_id)
        except Exception as ex:
            raise UserException(
                "Authorization failed, please try to reauthorize the configuration!") from ex

    def run(self):
        """
        Main execution code
        """

        self._init_configuration()

        destination: dict = self.configuration.parameters[KEY_DESTINATION]
        incremental: bool = LoadType(
            destination[KEY_LOAD_TYPE]) is LoadType.INCREMENTAL
        table_name: str = destination[KEY_OUTPUT_TABLE_NAME]

        os.makedirs(self.tables_out_path, exist_ok=True)

        object_type = ObjectType(
            self.configuration.parameters[KEY_OBJECT_TYPE])
        # Backward Compatibility
        account_id = self.configuration.parameters[KEY_AUTHORIZATION][KEY_ACCOUNT_ID]
        accounts = account_id if isinstance(account_id, list) else [account_id]

        for account in accounts:
            self._init_authorization(account_id=account)
            if object_type is ObjectType.ENTITY:
                download_request_config_dict: dict = self.configuration.parameters[
                    KEY_BULK_SETTINGS]
                download_request_class = BulkDownloadRequest
            elif object_type in (ObjectType.REPORT_CUSTOM, ObjectType.REPORT_PREBUILT):
                download_request_config_dict: dict = (self.configuration.parameters[KEY_REPORT_SETTINGS_CUSTOM]
                                                      if object_type is ObjectType.REPORT_CUSTOM else
                                                      self.configuration.parameters[KEY_REPORT_SETTINGS_PREBUILT])
                download_request_class = ReportDownloadRequest
            else:
                raise RuntimeError("Unexpected execution branch.")
            download_request: DownloadRequest = download_request_class(
                authorization=self.authorization,
                config_dict=download_request_config_dict,
                result_file_directory=self.tables_out_path,
                table_name=table_name,
                last_sync_time_in_utc=self.last_sync_time_in_utc,
            )

            download_request.process()

            self._slice_result(download_request.result_file_directory,
                               download_request.result_file_name, account)

            table_def = self.create_out_table_definition(
                download_request.result_file_name, incremental=incremental, is_sliced=True)
            table_def.primary_key = download_request.primary_key

            # Checking whether a CSV file was created
            if os.path.exists(table_def.full_path):
                self.write_manifest(table_def)

        # Extraction done, updating sync timestamp in state
        self.sync_time_in_utc_str = self.new_sync_time_in_utc_str
        self.save_state(self.authorization.refresh_token)  # type: ignore

    def _slice_result(self, full_path, file_name, account):
        slice_file_name = f"{account}{os.path.splitext(file_name)[1]}"
        slice_folder = f"{full_path}/{file_name}"
        os.rename(os.path.join(full_path, file_name),
                  os.path.join(full_path, slice_file_name))
        os.makedirs(slice_folder, exist_ok=True)
        os.rename(os.path.join(full_path, slice_file_name),
                  os.path.join(slice_folder, slice_file_name))

    def _validate_configuration(self):
        params: dict = self.configuration.parameters
        errors = []
        if not params.get(KEY_AUTHORIZATION, {}).get("account_id"):
            errors.append("Required parameter Account ID is missing!")
        if not params.get(KEY_AUTHORIZATION, {}).get("customer_id"):
            errors.append("Required parameter Customer ID is missing!")

        if not (object_type := params.get(KEY_OBJECT_TYPE, '')):
            errors.append("Required parameter Object Type is missing!")
        if object_type == 'entity':
            if not params.get(KEY_BULK_SETTINGS, {}).get('download_entities'):
                errors.append("You must select at least one Entity!")

        if object_type == 'report_custom':
            if not params.get(KEY_REPORT_SETTINGS_CUSTOM, {}).get('columns') and not params.get(
                    KEY_REPORT_SETTINGS_CUSTOM, {}).get('columns_array'):
                errors.append("You must select at least one column!")
            if not params.get(KEY_REPORT_SETTINGS_CUSTOM, {}).get('aggregation'):
                errors.append("You must select aggregation type!")

        if errors:
            raise UserException("\n".join(errors))

    @sync_action('get_report_columns')
    def get_report_columns(self):
        report_type = self.configuration.parameters.get(
            'report_settings_custom', {}).get('report_type')
        if not report_type:
            raise UserException('Report type is not specified!')
        available_cols = metadata_provider.get_report_available_columns()
        return [{"value": c, "label": c} for c in available_cols[report_type]]

    @sync_action('get_bulk_entities')
    def get_bulk_entities(self):
        available_cols = metadata_provider.get_available_bulk_entities()
        return [{"value": c, "label": c} for c in available_cols]

    @sync_action('get_accounts')
    def get_accounts(self):
        self._init_configuration()
        self._init_authorization()
        account_info: dict() = CustomerManagementServiceClient.get_accounts(self)  # type: ignore
        return [{"value": c.Id, "label": "AccountId"} for c in account_info]

    @sync_action('get_customer_id')
    def get_customer_id(self):
        self._init_configuration()
        self._init_authorization()
        user: dict() = CustomerManagementServiceClient.get_user(self)  # type: ignore
        return [{"value": user.CustomerId, "label": "CustomerId"}]

    def save_state(self, refresh_token: str):
        """
        Save refresh token to state file.
        """
        self.write_state_file({
            KEY_REFRESH_TOKEN: refresh_token,
            KEY_LAST_SYNC_TIME_IN_UTC: self.sync_time_in_utc_str,
        })

    def get_oauth_credentials(self) -> dict:
        return self.configuration.oauth_credentials  # type: ignore


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
