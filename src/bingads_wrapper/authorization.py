from dataclasses import dataclass, field
import logging
from typing import Callable, Literal, Optional

from bingads.authorization import (AuthorizationData, OAuthTokens, OAuthWithAuthorizationCode)
from bingads.exceptions import OAuthTokenRequestException

from keboola.component.dao import OauthCredentials

# User config params:
KEY_DEVELOPER_TOKEN = "#developer_token"
KEY_CUSTOMER_ID = "customer_id"
KEY_ACCOUNT_ID = "account_id"
KEY_ENVIRONMENT = "environment"


@dataclass(slots=True)
class Authorization:
    """
    Class to represent data needed to perform authorization with the API and performing it.
    """

    config_dict: dict
    oauth_credentials: OauthCredentials
    save_refresh_token_function: Callable[[str], None]
    refresh_token_from_state: Optional[str]

    authorization_data: AuthorizationData = field(init=False)
    developer_token: str = field(init=False)
    client_id: str = field(init=False)
    client_secret: Optional[str] = field(init=False)
    environment: Literal["sandbox", "production"] = field(init=False)
    refresh_token: str = field(init=False)
    customer_id: int = field(init=False)
    account_id: int = field(init=False)

    def __post_init__(self):
        self.client_id = self.oauth_credentials.appKey
        self.client_secret = self.oauth_credentials.appSecret
        self.refresh_token = self.oauth_credentials.data["refresh_token"]
        self.environment = self.config_dict[KEY_ENVIRONMENT]
        self.customer_id = self.config_dict[KEY_CUSTOMER_ID]
        self.account_id = self.config_dict[KEY_ACCOUNT_ID]
        self.developer_token = self.config_dict[KEY_DEVELOPER_TOKEN]

        authentication = OAuthWithAuthorizationCode(client_id=self.client_id,
                                                    client_secret=self.client_secret,
                                                    env=self.environment,
                                                    redirection_uri="",
                                                    token_refreshed_callback=self.save_refresh_token)

        try:
            authentication.request_oauth_tokens_by_refresh_token(self.refresh_token)
        except OAuthTokenRequestException:
            self.refresh_token = self.refresh_token_from_state
            authentication.request_oauth_tokens_by_refresh_token(self.refresh_token)
        logging.info("Refresh token authentication successful")

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
