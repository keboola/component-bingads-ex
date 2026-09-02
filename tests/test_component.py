"""
Created on 12. 11. 2018

@author: esner
"""
import json
import tempfile
import unittest
import mock
import os
from freezegun import freeze_time

from keboola.component.exceptions import UserException

from component import BingAdsExtractor


def _write_datadir(directory: str, destination: dict) -> None:
    """
    Write a minimal valid config.json into `directory`, with `destination` used verbatim.
    """
    os.makedirs(os.path.join(directory, "in"), exist_ok=True)
    config = {
        "parameters": {
            "authorization": {
                "account_id": "123456",
                "customer_id": "654321",
                "#developer_token": "dummy-token",
            },
            "object_type": "entity",
            "bulk_settings": {"download_entities": ["Campaigns"]},
            "destination": destination,
        }
    }
    with open(os.path.join(directory, "config.json"), "w") as config_file:
        json.dump(config, config_file)


class TestComponent(unittest.TestCase):

    # set global time to 2010-10-10 - affects functions like datetime.now()
    @freeze_time("2010-10-10")
    # set KBC_DATADIR env to non-existing dir
    @mock.patch.dict(os.environ, {"KBC_DATADIR": "./non-existing-dir"})
    def test_run_no_cfg_fails(self):
        with self.assertRaises(ValueError):
            comp = BingAdsExtractor()
            comp.run()


class TestDestinationValidation(unittest.TestCase):
    """
    A config whose `destination` has no `output_table_name` key used to reach
    `destination[KEY_OUTPUT_TABLE_NAME]` in run() and die with a bare KeyError,
    which the entrypoint turns into exit code 2 (internal error). It must fail as a
    UserException (exit code 1) instead - the job still fails, just legibly.
    """

    def test_missing_output_table_name_raises_user_exception(self):
        with tempfile.TemporaryDirectory() as datadir:
            _write_datadir(datadir, {"load_type": "full_load"})
            comp = BingAdsExtractor(data_path_override=datadir)

            with self.assertRaises(UserException) as ctx:
                comp.run()

            self.assertIn("output_table_name", str(ctx.exception))

    def test_empty_output_table_name_passes_validation(self):
        """
        An empty value is documented as valid ("Default object name used if left empty"),
        so the check above must be presence-only and must not reject it.
        """
        with tempfile.TemporaryDirectory() as datadir:
            _write_datadir(
                datadir, {"load_type": "full_load", "output_table_name": ""})
            comp = BingAdsExtractor(data_path_override=datadir)

            comp._init_configuration()


def _write_freshly_authorized_datadir(directory: str) -> None:
    """
    Write the config.json of a configuration that was only just authorized: OAuth is done,
    but the user has not saved the form yet, so `parameters` has no `authorization` section.
    """
    os.makedirs(os.path.join(directory, "in"), exist_ok=True)
    config = {
        "parameters": {},
        "image_parameters": {"developer_token": "dummy-token"},
        "authorization": {
            "oauth_api": {
                "credentials": {
                    "id": "main",
                    "authorizedFor": "test",
                    "appKey": "dummy-app-key",
                    "#appSecret": "dummy-app-secret",
                    "#data": json.dumps({"refresh_token": "dummy-refresh-token"}),
                }
            }
        },
    }
    with open(os.path.join(directory, "config.json"), "w") as config_file:
        json.dump(config, config_file)


class TestSyncActionsAfterOauth(unittest.TestCase):
    """
    Right after the OAuth authorization the configuration has no `parameters.authorization`
    section. The Customer ID field autoloads the `get_customers` sync action as soon as the
    form opens, so the sync action ran against that configuration and failed with
    "Missing mandatory config parameters fields: [authorization]", which left both the
    Customer ID and the Account ID dropdowns empty.
    """

    def test_init_configuration_accepts_empty_parameters_in_sync_action(self):
        with tempfile.TemporaryDirectory() as datadir:
            _write_freshly_authorized_datadir(datadir)
            comp = BingAdsExtractor(data_path_override=datadir)

            comp._init_configuration(from_sync_action=True)

    def test_init_configuration_still_rejects_empty_parameters_in_run(self):
        """
        The run() path must keep failing on a configuration with no authorization section.
        """
        with tempfile.TemporaryDirectory() as datadir:
            _write_freshly_authorized_datadir(datadir)
            comp = BingAdsExtractor(data_path_override=datadir)

            with self.assertRaises(UserException):
                comp._init_configuration()

    @mock.patch("component.Authorization")
    def test_init_authorization_without_authorization_section(self, authorization_mock):
        """
        The developer token comes from the image parameters, so authorization can be built
        with no `parameters.authorization` section at all.
        """
        with tempfile.TemporaryDirectory() as datadir:
            _write_freshly_authorized_datadir(datadir)
            comp = BingAdsExtractor(data_path_override=datadir)

            comp._init_authorization()

            config_dict = authorization_mock.call_args.kwargs["config_dict"]
            self.assertEqual("dummy-token", config_dict["#developer_token"])
            # The live configuration must not gain a developer token as a side effect.
            self.assertEqual({}, comp.configuration.parameters)


class TestConfigSchema(unittest.TestCase):

    def test_account_autoload_watches_the_real_customer_id_path(self):
        """
        Autoload paths are resolved from the configuration root. `customer_id` lives in the
        authorization section, so a path of `parameters.customer_id` never matched and the
        Account ID list was never reloaded after a customer was picked.
        """
        schema_path = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "component_config", "configSchema.json")
        with open(schema_path) as schema_file:
            schema = json.load(schema_file)

        account_id = schema["properties"]["authorization"]["properties"]["account_id"]
        self.assertEqual(["parameters.authorization.customer_id"],
                         account_id["options"]["async"]["autoload"])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
