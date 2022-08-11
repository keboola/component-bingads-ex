from dataclasses import dataclass
from typing import Callable, Literal, Optional
import webbrowser

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
        get_user_response = customer_service.GetUser(UserId=None)
        return get_user_response.User
