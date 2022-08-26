"""
Template Component main class.

"""
import logging
import os
import secrets
import string
from typing import Optional

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

# Other constants
NONCE_LENGTH = 32


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
        )
        download_request.process()

        self.write_manifest(table_def)

        # customer_management_service_client = CustomerManagementServiceClient(
        #     authorization=authorization
        # )
        # user = customer_management_service_client.get_user()
        # logging.info(user)

        # ###### EXAMPLE TO REMOVE START
        # # Create output table (Tabledefinition - just metadata)
        # table = self.create_out_table_definition(
        #     "output.csv", incremental=True, primary_key=["timestamp"]
        # )

        # # get file path of the table (data/out/tables/Features.csv)
        # out_table_path = table.full_path
        # logging.info(out_table_path)
        # # DO whatever and save into out_table_path
        # with open(table.full_path, mode="wt", encoding="utf-8", newline="") as out_file:
        #     writer = csv.DictWriter(out_file, fieldnames=["timestamp"])
        #     writer.writeheader()
        #     writer.writerow({"timestamp": datetime.now().isoformat()})

        # # Save table manifest (output.csv.manifest) from the tabledefinition
        # self.write_manifest(table)

        # # Write new state - will be available next run TODO: extract into method
        # self.write_state_file({KEY_REFRESH_TOKEN: refresh_token, KEY_NONCE: nonce})

        # ####### EXAMPLE TO REMOVE END

    def save_state(self, refresh_token: str):
        """
        Save refresh token and nonce to state file.
        """
        self.write_state_file({KEY_REFRESH_TOKEN: refresh_token, KEY_NONCE: self.nonce})


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
