"""
Tests for the move from the SOAP API to the REST API.

These cover the parts the transport change touches: building a report request, reading
the report and bulk metadata, and turning an API error into a UserException.
"""

import unittest
import warnings

import openapi_client.models as rest_models
from bingads.authorization import AuthorizationData
from keboola.component.exceptions import UserException
from openapi_client.exceptions import ApiException

from bingads_wrapper import metadata_provider
from bingads_wrapper.error_handling import process_api_errors
from bingads_wrapper.reporting import ReportingDownloadParametersFactory
from bingads_wrapper.rest_compat import UnsupportedReportTypeError, create_report_request

ACCOUNT_ID = 424242


class _FakeAuthentication:
    def enrich_headers(self, headers):
        headers["Authorization"] = "Bearer test"


def _authorization_data() -> AuthorizationData:
    return AuthorizationData(
        account_id=ACCOUNT_ID,
        customer_id=1,
        developer_token="test-token",
        authentication=_FakeAuthentication(),
    )


def _build_report_request(config: dict):
    factory = ReportingDownloadParametersFactory(
        authorization_data=_authorization_data(),
        config_dict=config,
        result_file_directory="/tmp",
        report_file_format="Csv",
        result_file_name=None,
        last_sync_time_in_utc=None,
    )
    return factory, factory.create().report_request


def _predefined_config(report_type="SearchQueryPerformance") -> dict:
    return {
        "report_type": report_type,
        "aggregation": "Daily",
        "return_only_complete_data": False,
        "time_range": {"time_zone": "PacificTimeUSCanadaTijuana", "period": "LastSevenDays"},
        "columns_array": ["Clicks", "Impressions", "TimePeriod"],
        "primary_key_array": ["TimePeriod"],
    }


class TestReportRequestBuilding(unittest.TestCase):
    def test_builds_the_request_model_for_the_report_type(self):
        _, report_request = _build_report_request(_predefined_config())
        self.assertIsInstance(report_request, rest_models.SearchQueryPerformanceReportRequest)

    def test_sets_the_base_parameters(self):
        _, report_request = _build_report_request(_predefined_config())
        payload = report_request.model_dump(by_alias=True, exclude_none=True)
        self.assertEqual(payload["Format"], "Csv")
        self.assertEqual(payload["FormatVersion"], "2.0")
        self.assertIs(payload["ExcludeReportHeader"], True)
        self.assertIs(payload["ExcludeReportFooter"], True)
        self.assertIs(payload["ExcludeColumnHeaders"], False)

    def test_sets_a_predefined_time_range(self):
        _, report_request = _build_report_request(_predefined_config())
        payload = report_request.model_dump(by_alias=True, exclude_none=True)
        self.assertEqual(payload["Time"]["PredefinedTime"], "LastSevenDays")
        self.assertEqual(payload["Time"]["ReportTimeZone"], "PacificTimeUSCanadaTijuana")
        self.assertNotIn("CustomDateRangeStart", payload["Time"])

    def test_sets_a_custom_date_range(self):
        config = _predefined_config()
        config["time_range"] = {
            "time_zone": "PacificTimeUSCanadaTijuana",
            "period": "CustomTimeRange",
            "date_from": "2026-01-02",
            "date_to": "2026-01-31",
        }
        _, report_request = _build_report_request(config)
        time = report_request.model_dump(by_alias=True, exclude_none=True)["Time"]
        self.assertEqual(time["CustomDateRangeStart"], {"Year": 2026, "Month": 1, "Day": 2})
        self.assertEqual(time["CustomDateRangeEnd"], {"Year": 2026, "Month": 1, "Day": 31})

    def test_sends_the_account_id_as_a_string_in_the_scope(self):
        # The REST models declare AccountIds as a list of strings and validate on
        # assignment, so an integer account id would be rejected.
        _, report_request = _build_report_request(_predefined_config())
        payload = report_request.model_dump(by_alias=True, exclude_none=True)
        self.assertEqual(payload["Scope"]["AccountIds"], [str(ACCOUNT_ID)])

    def test_uses_the_scope_type_that_the_report_declares(self):
        # Scope is AccountReportScope on some reports and AccountThroughAdGroupReportScope
        # on others, so the type is resolved per report type.
        _, account_report = _build_report_request(_predefined_config("AccountPerformance"))
        _, search_report = _build_report_request(_predefined_config("SearchQueryPerformance"))
        self.assertIsInstance(account_report.Scope, rest_models.AccountReportScope)
        self.assertIsInstance(search_report.Scope, rest_models.AccountThroughAdGroupReportScope)

    def test_adds_the_account_id_column_and_keeps_the_configured_columns(self):
        factory, report_request = _build_report_request(_predefined_config())
        columns = report_request.model_dump(by_alias=True, exclude_none=True)["Columns"]
        self.assertEqual(columns, ["Clicks", "Impressions", "TimePeriod", "AccountId"])
        self.assertEqual(factory.primary_key, ["TimePeriod", "AccountId"])

    def test_converts_values_to_the_enum_members_the_model_declares(self):
        # A plain string left on an enum field serializes with a warning and leaves the
        # model inconsistent, so the values are converted when they are set.
        with warnings.catch_warnings():
            warnings.simplefilter("error", UserWarning)
            _, report_request = _build_report_request(_predefined_config())
            report_request.model_dump(by_alias=True, exclude_none=True)

    def test_rejects_a_report_type_the_api_does_not_have(self):
        with self.assertRaises(UnsupportedReportTypeError):
            create_report_request("NoSuchThing")

    def test_requires_the_primary_key_to_be_a_subset_of_the_columns(self):
        config = _predefined_config()
        config["primary_key_array"] = ["CampaignName"]
        with self.assertRaises(UserException):
            _build_report_request(config)


class TestMetadataProvider(unittest.TestCase):
    def test_lists_report_columns_without_reading_the_soap_proxy_files(self):
        columns = metadata_provider.get_report_available_columns()
        self.assertIn("SearchQueryPerformance", columns)
        self.assertIn("AccountId", columns["SearchQueryPerformance"])
        self.assertTrue(all(values for values in columns.values()))

    def test_lists_bulk_entities_and_hides_the_none_placeholder(self):
        entities = metadata_provider.get_available_bulk_entities()
        self.assertIn("Campaigns", entities)
        self.assertNotIn("None", entities)


class TestErrorHandling(unittest.TestCase):
    def test_reports_the_api_error_message(self):
        error = ApiException(status=400, reason="Bad Request")
        error.body = '{"Errors": [{"Code": 105, "Message": "Invalid credentials."}]}'
        with self.assertRaises(UserException) as caught:
            process_api_errors(error)
        self.assertIn("Invalid credentials.", str(caught.exception))

    def test_reports_every_operation_error(self):
        error = ApiException(status=400, reason="Bad Request")
        error.body = (
            '{"OperationErrors": ['
            '{"Message": "First problem.", "Details": "detail one"},'
            '{"Message": "Second problem."}]}'
        )
        with self.assertRaises(UserException) as caught:
            process_api_errors(error)
        message = str(caught.exception)
        self.assertIn("detail one", message)
        self.assertIn("First problem.", message)
        self.assertIn("Second problem.", message)

    def test_keeps_the_status_when_the_body_is_not_recognised(self):
        # The failure must stay diagnosable instead of surfacing as an empty message.
        error = ApiException(status=503, reason="Service Unavailable")
        error.body = "<html>gateway error</html>"
        with self.assertRaises(UserException) as caught:
            process_api_errors(error)
        message = str(caught.exception)
        self.assertIn("503", message)
        self.assertNotEqual(message.strip(), "")


class TestSyncActionLabels(unittest.TestCase):
    def test_shows_the_plain_enum_value(self):
        # str() on an enum member would render "AccountLifeCycleStatus.ACTIVE".
        from component import _enum_value

        self.assertEqual(_enum_value(rest_models.AccountLifeCycleStatus.ACTIVE), "Active")
        self.assertEqual(_enum_value("Active"), "Active")


if __name__ == "__main__":
    unittest.main()
