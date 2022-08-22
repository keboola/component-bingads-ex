"""
Template Component main class.

"""
import logging
import os
import secrets
import string
from typing import Literal, Optional

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

from client import BingAdsClient

# configuration variables
KEY_CLIENT_ID = "client_id"
KEY_DEVELOPER_TOKEN = "#developer_token"
KEY_CUSTOMER_ID = "customer_id"
KEY_ACCOUNT_ID = "account_id"
KEY_ENVIRONMENT = "environment"

# list of mandatory parameters => if some is missing,
# component will fail with readable message on initialization.
REQUIRED_PARAMETERS = [KEY_CLIENT_ID, KEY_DEVELOPER_TOKEN, KEY_ENVIRONMENT]
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

    # def __init__(self):
    #     super().__init__()

    def run(self):
        """
        Main execution code
        """
        self.validate_configuration_parameters(REQUIRED_PARAMETERS)
        self.validate_image_parameters(REQUIRED_IMAGE_PARS)

        params = self.configuration.parameters
        client_id: str = params[KEY_CLIENT_ID]
        developer_token: str = params[KEY_DEVELOPER_TOKEN]
        environment: Literal["sandbox", "production"] = params[KEY_ENVIRONMENT]
        customer_id: int = params[KEY_CUSTOMER_ID]
        account_id: int = params[KEY_ACCOUNT_ID]

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

        bing_ads_client = BingAdsClient(
            client_id=client_id,
            developer_token=developer_token,
            environment=environment,
            customer_id=customer_id,
            account_id=account_id,
            refresh_token=refresh_token,
            nonce=self.nonce,
            save_refresh_token_function=self.save_state,
        )
        user = bing_ads_client.get_user()
        print(user)
        bulk_download_operation = bing_ads_client.submit_download()
        print(bulk_download_operation)
        download_status = bulk_download_operation.track()
        os.makedirs(self.tables_out_path, exist_ok=True)
        result_file_path = bulk_download_operation.download_result_file(
            result_file_directory=self.tables_out_path,
            result_file_name="result.csv",
            decompress=True,
            overwrite=True,  # Set this value true if you want to overwrite the same file.
            timeout_in_milliseconds=10000,  # You may optionally cancel the download after a specified time interval.
        )
        pass
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
