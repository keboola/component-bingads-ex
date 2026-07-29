"""
Covers the fault-formatting fixes: AdApiError's numeric Code / symbolic ErrorCode /
singular Detail must survive into the error message, and Microsoft's TrackingId must
not be dropped when a fault carries structured detail.
"""
import unittest

from keboola.component import UserException
from suds import WebFault
from suds.sudsobject import Object

from bingads_wrapper.error_handling import (get_tracking_id, get_webfault_error_message,
                                           process_webfault_errors)

# The fault Microsoft returns for an authentication failure, as observed on
# CustomerManagementService.GetUser.
AUTH_FAILED_MESSAGE = "Authentication failed. Either supplied credentials are invalid or the account is inactive"
TRACKING_ID = "2ea292d0-c063-4269-9d3a-39b77e43f01a"
FAULTSTRING = (f"Invalid client data. Check the SOAP fault details for more information. "
               f"TrackingId: {TRACKING_ID}.")


def make_ad_api_error(code=105, error_code="InvalidCredentials", detail=None,
                      message=AUTH_FAILED_MESSAGE):
    error = Object()
    error.Code = code
    error.ErrorCode = error_code
    error.Detail = detail
    error.Message = message
    return error


def make_webfault(errors, faultstring=FAULTSTRING):
    """Build a WebFault shaped like the AdApiFaultDetail one the API returns."""
    ad_api_fault_detail = Object()
    ad_api_fault_detail.Errors = Object()
    ad_api_fault_detail.Errors.AdApiError = errors

    detail = Object()
    detail.AdApiFaultDetail = ad_api_fault_detail

    fault = Object()
    fault.faultstring = faultstring
    fault.detail = detail
    return WebFault(fault, document=None)


class TestGetWebfaultErrorMessage(unittest.TestCase):

    def test_ad_api_error_keeps_code_and_error_code(self):
        message = get_webfault_error_message(make_ad_api_error())
        self.assertIn("Code: 105", message)
        self.assertIn("ErrorCode: InvalidCredentials", message)
        self.assertIn(AUTH_FAILED_MESSAGE, message)

    def test_ad_api_error_keeps_singular_detail(self):
        message = get_webfault_error_message(make_ad_api_error(detail="UserNotFound"))
        self.assertIn("UserNotFound", message)

    def test_empty_detail_is_not_emitted(self):
        message = get_webfault_error_message(make_ad_api_error(detail=None))
        self.assertNotIn("None", message)

    def test_code_zero_is_still_emitted(self):
        # 0 is falsy but a legitimate code, so it must not be filtered out.
        message = get_webfault_error_message(make_ad_api_error(code=0))
        self.assertIn("Code: 0", message)

    def test_operation_error_plural_details_still_work(self):
        error = Object()
        error.Code = 117
        error.Details = "CampaignServiceEditorialError"
        error.Message = "The operation failed."
        message = get_webfault_error_message(error)
        self.assertIn("Code: 117", message)
        self.assertIn("CampaignServiceEditorialError", message)
        self.assertIn("The operation failed.", message)


class TestGetTrackingId(unittest.TestCase):

    def test_extracts_tracking_id(self):
        fault = Object()
        fault.faultstring = FAULTSTRING
        self.assertEqual(get_tracking_id(fault), TRACKING_ID)

    def test_returns_empty_when_absent(self):
        fault = Object()
        fault.faultstring = "Some fault without a tracking id."
        self.assertEqual(get_tracking_id(fault), "")

    def test_returns_empty_when_no_faultstring(self):
        self.assertEqual(get_tracking_id(Object()), "")


class TestProcessWebfaultErrors(unittest.TestCase):

    def test_raises_user_exception_with_full_detail(self):
        with self.assertRaises(UserException) as context:
            process_webfault_errors(make_webfault(make_ad_api_error()))
        message = str(context.exception)
        self.assertIn("Code: 105", message)
        self.assertIn("ErrorCode: InvalidCredentials", message)
        self.assertIn(AUTH_FAILED_MESSAGE, message)
        self.assertIn(f"TrackingId: {TRACKING_ID}", message)

    def test_handles_list_of_errors(self):
        errors = [make_ad_api_error(), make_ad_api_error(code=109, error_code="AuthenticationTokenExpired",
                                                        message="Authentication token expired.")]
        with self.assertRaises(UserException) as context:
            process_webfault_errors(make_webfault(errors))
        message = str(context.exception)
        self.assertIn("Code: 105", message)
        self.assertIn("ErrorCode: AuthenticationTokenExpired", message)

    def test_no_tracking_id_leaves_message_unchanged(self):
        with self.assertRaises(UserException) as context:
            process_webfault_errors(make_webfault(make_ad_api_error(), faultstring="Nothing useful."))
        message = str(context.exception)
        self.assertNotIn("TrackingId", message)
        self.assertIn(AUTH_FAILED_MESSAGE, message)


if __name__ == "__main__":
    unittest.main()
