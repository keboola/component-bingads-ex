from dataclasses import dataclass, field
import time
from typing import Callable, List, Literal, Optional
import webbrowser

from suds import WebFault

from bingads.service_client import ServiceClient
from bingads.authorization import (
    AuthorizationData,
    OAuthDesktopMobileAuthCodeGrant,
    OAuthTokens,
    OAuthWithAuthorizationCode,
)
from bingads.v13.bulk import (
    BulkServiceManager,
    SubmitDownloadParameters,
    BulkDownloadOperation,
    BulkOperationStatus,
)

# from bingads.v13.reporting import (
#     ReportingServiceManager,
#     ReportingDownloadParameters,
#     ReportingDownloadOperation,
# )

DOWNLOAD_REQUEST_TIMEOUT_PERIOD_MILLISECONDS = 60 * 1000


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
    for _field in error_attribute_set:
        api_errors = getattr(api_errors, _field, None)
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


@dataclass(slots=True, frozen=True)
class DownloadRequestSpec:
    data_scope: List[str]
    download_entities: List[str]


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
    __authorization_data: Optional[AuthorizationData] = field(init=False)

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

        self.__authorization_data = AuthorizationData(
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
            authorization_data=self.__authorization_data,
            environment=self.environment,
        )
        try:
            get_user_response = customer_service.GetUser(UserId=None)
        except WebFault as ex:
            output_webfault_errors(ex)

        return get_user_response.User

    def submit_download(
        self, data_scope: List[str], download_entities: List[str]
    ) -> BulkDownloadOperation:
        bulk_service_manager = BulkServiceManager(
            authorization_data=self.__authorization_data, environment=self.environment
        )
        submit_download_parameters = SubmitDownloadParameters(
            campaign_ids=None,
            data_scope=data_scope,
            download_entities=download_entities,
            file_type="Csv",
            last_sync_time_in_utc=None,
        )
        try:
            bulk_download_operation = bulk_service_manager.submit_download(
                submit_download_parameters
            )
        except WebFault as ex:
            output_webfault_errors(ex)

        return bulk_download_operation

    def get_download_status(
        self, bulk_download_operation: BulkDownloadOperation
    ) -> BulkOperationStatus:
        try:
            bulk_operation_status = bulk_download_operation.get_status()
        except WebFault as ex:
            output_webfault_errors(ex)

        return bulk_operation_status

    def download_file(
        self,
        bulk_download_operation: BulkDownloadOperation,
        directory: str,
        filename: str,
    ) -> str:
        try:
            filepath = bulk_download_operation.download_result_file(
                result_file_directory=directory,
                result_file_name=filename,
                decompress=True,
                overwrite=True,
                timeout_in_milliseconds=DOWNLOAD_REQUEST_TIMEOUT_PERIOD_MILLISECONDS,
            )
        except WebFault as ex:
            output_webfault_errors(ex)

        return filepath

    def perform_all_download_operations(
        self,
        bulk_download_operation_specs: List[DownloadRequestSpec],
        download_directory: str,
        filename_prefix: str,
    ):
        """
        Perform all download operations.
        """
        bulk_download_operations = [
            self.submit_download(
                data_scope=spec.data_scope, download_entities=spec.download_entities
            )
            for spec in bulk_download_operation_specs
        ]
        all_done = False
        bulk_download_operations_to_be_completed = bulk_download_operations.copy()
        bulk_download_operations_to_be_removed: List[BulkDownloadOperation] = []
        completed_downloads = 0
        while not all_done:
            all_done = True
            time.sleep(1)
            for bulk_download_operation in bulk_download_operations_to_be_removed:
                bulk_download_operations_to_be_completed.remove(bulk_download_operation)
                bulk_download_operations_to_be_removed.remove(bulk_download_operation)
            for bulk_download_operation in bulk_download_operations_to_be_completed:
                bulk_operation_status = self.get_download_status(
                    bulk_download_operation
                )
                if bulk_operation_status.status == "InProgress":
                    all_done = False
                elif bulk_operation_status.status == "Failed":
                    raise Exception(
                        "Download operation failed with status: {0}".format(
                            bulk_operation_status.status
                        )
                    )
                elif bulk_operation_status.status == "Completed":
                    self.download_file(
                        bulk_download_operation=bulk_download_operation,
                        directory=download_directory,
                        filename=filename_prefix + str(completed_downloads) + ".csv",
                    )
                    completed_downloads += 1
                    bulk_download_operations_to_be_removed.append(
                        bulk_download_operation
                    )
                else:
                    raise Exception(
                        "Download operation failed with status: {0}".format(
                            bulk_operation_status.status
                        )
                    )
