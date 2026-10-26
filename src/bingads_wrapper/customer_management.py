from dataclasses import dataclass

from bingads.service_client import ServiceClient
from openapi_client.exceptions import ApiException
from openapi_client.models import (
    GetAccountsInfoRequest,
    GetCustomerRequest,
    GetUserRequest,
)

from .authorization import Authorization
from .error_handling import process_api_errors

# Imported for the side effect of enabling PascalCase field access on the REST models.
from . import rest_compat  # noqa: F401


@dataclass(slots=True)
class CustomerManagementServiceClient:
    authorization: Authorization

    def _service(self) -> ServiceClient:
        return ServiceClient(
            service="CustomerManagementService",
            version=13,
            authorization_data=self.authorization.authorization_data,
            environment=self.authorization.environment,
        )

    def get_user(self):
        """
        Get the authenticated user.
        """
        customer_service = self._service()
        try:
            get_user_response = customer_service.GetUser(GetUserRequest(UserId=None))
            user = get_user_response.User
            return user
        except ApiException as ex:
            process_api_errors(ex)

    def get_accounts(self):
        """
        Get accounts for the authenticated user.
        """
        customer_service = self._service()
        try:
            get_account_response = customer_service.GetAccountsInfo(
                GetAccountsInfoRequest(CustomerId=_as_api_id(self.authorization.customer_id))
            )
            # REST names this collection "AccountsInfo". SOAP named it "AccountInfo" and
            # wrapped it in an ArrayOfAccountInfo element. The value is now a plain list.
            account_info = get_account_response.AccountsInfo or []
            return account_info
        except ApiException as ex:
            process_api_errors(ex)

    def get_customers(self):
        """
        Get customers for the authenticated user.
        """
        customer_service = self._service()
        try:
            get_user_response = customer_service.GetUser(GetUserRequest(UserId=None))
        except ApiException as ex:
            process_api_errors(ex)
        response = []
        # REST returns CustomerRoles as a plain list. SOAP wrapped it in an
        # ArrayOfCustomerRole element, which is why the SOAP build read .CustomerRole.
        for customer_role in get_user_response.CustomerRoles or []:
            try:
                get_customer_response = customer_service.GetCustomer(
                    GetCustomerRequest(CustomerId=_as_api_id(customer_role.CustomerId))
                )
                # The caller reads .Id, .Name and .Number, which live on the Customer
                # itself and not on the response envelope.
                response.append(get_customer_response.Customer)
            except ApiException as ex:
                process_api_errors(ex)
        return response


def _as_api_id(value):
    """
    Return an id in the type the REST models declare.

    The REST models type account and customer ids as strings and validate on assignment,
    so an integer id raises a validation error. The SOAP build accepted both.
    """
    return None if value is None else str(value)
