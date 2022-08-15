from dataclasses import dataclass
from typing import Callable, Literal, Optional
import webbrowser

from suds import WebFault

from bingads.service_client import ServiceClient
from bingads.authorization import (
    AuthorizationData,
    OAuthDesktopMobileAuthCodeGrant,
    OAuthTokens,
    OAuthWithAuthorizationCode,
)


def request_user_consent(authentication: OAuthWithAuthorizationCode):
    webbrowser.open(authentication.get_authorization_endpoint(), new=1)
    response_uri = input(
        "You need to provide consent for the application to access your Microsoft Advertising accounts."
        " After you have granted consent in the web browser for the application"
        " to access your Microsoft Advertising accounts,"
        " please enter the response URI that includes the authorization 'code' parameter: \n"
    )
    # Request access and refresh tokens using the URI that you provided manually during program execution.
    authentication.request_oauth_tokens_by_response_uri(response_uri=response_uri)


def output_status_message(message):
    print(message)


def output_bing_ads_webfault_error(error):
    if hasattr(error, "ErrorCode"):
        output_status_message("ErrorCode: {0}".format(error.ErrorCode))
    if hasattr(error, "Code"):
        output_status_message("Code: {0}".format(error.Code))
    if hasattr(error, "Details"):
        output_status_message("Details: {0}".format(error.Details))
    if hasattr(error, "FieldPath"):
        output_status_message("FieldPath: {0}".format(error.FieldPath))
    if hasattr(error, "Message"):
        output_status_message("Message: {0}".format(error.Message))
    output_status_message("")


def output_error_detail(error_detail, error_attribute_set):
    api_errors = error_detail
    for field in error_attribute_set:
        api_errors = getattr(api_errors, field, None)
    if api_errors is None:
        return False
    if isinstance(api_errors, list):
        for api_error in api_errors:
            output_bing_ads_webfault_error(api_error)
    else:
        output_bing_ads_webfault_error(api_errors)
    return True


def output_webfault_errors(ex):
    if not hasattr(ex.fault, "detail"):
        raise Exception("Unknown WebFault")

    error_attribute_sets = (
        ["ApiFault", "OperationErrors", "OperationError"],
        ["AdApiFaultDetail", "Errors", "AdApiError"],
        ["ApiFaultDetail", "BatchErrors", "BatchError"],
        ["ApiFaultDetail", "OperationErrors", "OperationError"],
        ["EditorialApiFaultDetail", "BatchErrors", "BatchError"],
        ["EditorialApiFaultDetail", "EditorialErrors", "EditorialError"],
        ["EditorialApiFaultDetail", "OperationErrors", "OperationError"],
    )

    for error_attribute_set in error_attribute_sets:
        if output_error_detail(ex.fault.detail, error_attribute_set):
            return

    # Handle serialization errors, for example:
    # The formatter threw an exception while trying to deserialize the message, etc.
    if hasattr(ex.fault, "detail") and hasattr(ex.fault.detail, "ExceptionDetail"):
        api_errors = ex.fault.detail.ExceptionDetail
        if isinstance(api_errors, list):
            for api_error in api_errors:
                output_status_message(api_error.Message)
        else:
            output_status_message(api_errors.Message)
        return

    raise Exception("Unknown WebFault")


@dataclass(slots=True)
class BingAdsClient:
    """
    Class to represent a Bing Ads client.
    """

    client_id: str
    developer_token: str
    environment: Literal["sandbox", "production"]
    save_refresh_token_function: Callable[[str], None]
    customer_id: Optional[str]
    account_id: Optional[str]
    refresh_token: Optional[str] = None
    nonce: Optional[str] = None
    authorization_data: Optional[AuthorizationData] = None

    def __post_init__(self):
        authentication = OAuthDesktopMobileAuthCodeGrant(
            client_id=self.client_id, env=self.environment
        )
        authentication.state = self.nonce
        authentication.token_refreshed_callback = self.save_refresh_token

        if self.refresh_token:
            authentication.request_oauth_tokens_by_refresh_token(self.refresh_token)
        else:
            # This branch should only be reached when the program is run in a development environment,
            #  otherwise refresh_token must be set. TODO: implement a check for this.
            request_user_consent(authentication)

        self.authorization_data = AuthorizationData(
            account_id=self.account_id,
            customer_id=self.customer_id,
            developer_token=self.developer_token,
            authentication=authentication,
        )

    def save_refresh_token(self, oauth_tokens: OAuthTokens) -> None:
        """
        Save the refresh token in the state file.
        """
        self.refresh_token = oauth_tokens.refresh_token
        self.save_refresh_token_function(self.refresh_token)

    def get_user(self):
        """
        Get the authenticated user.
        """
        customer_service = ServiceClient(
            service="CustomerManagementService",
            version=13,
            authorization_data=self.authorization_data,
            environment=self.environment,
        )
        try:
            get_user_response = customer_service.GetUser(UserId=None)
        except WebFault as ex:
            output_webfault_errors(ex)

        return get_user_response.User

    def get_campaigns(self):
        bulk_service = ServiceClient(
            service="BulkService",
            version=13,
            authorization_data=self.authorization_data,
            environment=self.environment,
        )
        try:
            get_campaigns_response = bulk_service.DownloadCampaignsByAccountIds()
        except WebFault as ex:
            output_webfault_errors(ex)

        return get_campaigns_response
