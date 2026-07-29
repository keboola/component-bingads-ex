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


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
