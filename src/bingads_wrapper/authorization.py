from dataclasses import dataclass, field
import logging
from typing import Callable, Literal, Optional
import webbrowser

from bingads.authorization import (
    AuthorizationData,
    OAuthDesktopMobileAuthCodeGrant,
    OAuthTokens,
    OAuthWithAuthorizationCode,
)

KEY_CLIENT_ID = "client_id"
KEY_DEVELOPER_TOKEN = "#developer_token"
KEY_CUSTOMER_ID = "customer_id"
KEY_ACCOUNT_ID = "account_id"
KEY_ENVIRONMENT = "environment"


def request_user_consent(authentication: OAuthWithAuthorizationCode):
    webbrowser.open(authentication.get_authorization_endpoint(), new=1)
    response_uri = input(
        "You need to provide consent for the application to access your Microsoft Advertising accounts."
        " After you have granted consent in the web browser for the application"
        " to access your Microsoft Advertising accounts,"
        " please enter the response URI that includes the authorization 'code' parameter: \n")
    # Request access and refresh tokens using the URI that you provided manually during program execution.
    authentication.request_oauth_tokens_by_response_uri(response_uri=response_uri)


@dataclass(slots=True)
class Authorization:
    """
    Class to represent data needed to perform authorization with the API and performing it.
    """

    config_dict: dict
    save_refresh_token_function: Callable[[str], None]
    refresh_token: Optional[str] = None
    nonce: Optional[str] = None

    authorization_data: AuthorizationData = field(init=False)
    client_id: str = field(init=False)
    developer_token: str = field(init=False)
    environment: Literal["sandbox", "production"] = field(init=False)
    customer_id: int = field(init=False)
    account_id: int = field(init=False)

    def __post_init__(self):
        self.client_id = self.config_dict[KEY_CLIENT_ID]
        self.developer_token = self.config_dict[KEY_DEVELOPER_TOKEN]
        self.environment = self.config_dict[KEY_ENVIRONMENT]
        self.customer_id = self.config_dict[KEY_CUSTOMER_ID]
        self.account_id = self.config_dict[KEY_ACCOUNT_ID]

        authentication = OAuthDesktopMobileAuthCodeGrant(client_id=self.client_id, env=self.environment)
        authentication.state = self.nonce
        authentication.token_refreshed_callback = self.save_refresh_token

        if self.refresh_token:
            authentication.request_oauth_tokens_by_refresh_token(self.refresh_token)
            logging.info("Refresh token authentication successful")
        else:
            # This branch should only be reached when the program is run in a development environment,
            #  otherwise refresh_token must be set. TODO: implement a check for this and raise user error.
            request_user_consent(authentication)
            logging.info("User consent acquired successfully")

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
        logging.info("Refresh token saved successfully")
