from dataclasses import dataclass

from bingads.service_client import ServiceClient

from suds import WebFault

from .authorization import Authorization
from .error_handling import process_webfault_errors


@dataclass(slots=True)
class CustomerManagementServiceClient:
    authorization: Authorization

    def get_user(self):
        """
        Get the authenticated user.
        """

        customer_service = ServiceClient(
            service="CustomerManagementService",
            version=13,
            authorization_data=self.authorization.authorization_data,
            environment=self.authorization.environment,
        )
        try:
            get_user_response = customer_service.GetUser(UserId=None)
            #user = get_user_response.User
            return get_user_response
        except WebFault as ex:
            process_webfault_errors(ex)

    def get_accounts(self):
        """
        Get accounts for the authenticated user.
        """
        customer_service = ServiceClient(
            service="CustomerManagementService",
            version=13,
            authorization_data=self.authorization.authorization_data,
            environment=self.authorization.environment,
        )
        try:
            get_account_response = customer_service.GetAccountsInfo(
                CustomerId=None)
            account_info = get_account_response.AccountInfo
            return account_info
        except WebFault as ex:
            process_webfault_errors(ex)
