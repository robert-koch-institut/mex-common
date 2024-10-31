from mex.common.connector.http import HTTPConnector
from mex.common.settings import BaseSettings


class OrcidConnector(HTTPConnector):  # noqa: D101
    # TODO:  # noqa: TD002
    # oauth with orcid sandbox to get oauth code
    # get read-public key
    # OrcidPerson class
    # refine session and requests for person here
    def __init__(self) -> None:  # noqa: D107
        # Define the URL and the data
        url = "https://sandbox.orcid.org/oauth/token"  # noqa: F841
        headers = {"Accept": "application/json"}
        data = {
            "client_id": "APP-Q0MJ2SJAAVUW563V",
            "client_secret": "0e64a343-4e76-46ae-9bac-e6d668b2ea29",
            "grant_type": "authorization_code",
            "redirect_uri": "REPLACE WITH REDIRECT URI",
            "code": "REPLACE WITH OAUTH CODE",
        }

        # Make the POST request
        self.request(method="POST", payload=data, headers=headers)
        super().__init__()

    def _set_url(self) -> None:
        """Set url of the host."""
        settings = BaseSettings.get()
        self.url = str(settings.orcid_api_url)

    def _set_authentication(self) -> None:
        settings = BaseSettings.get()  # noqa: F841
        params = {"format": "json"}
        headers = {
            "Accept": "application/json",
        }
        payload = {
            "client_id": "APP-VR547LITRBDHPQS8",
            "client_secret": "061f843e-3aa5-41b3-bce3-d87e3f3906f8",
            "grant_type": "client_credentials",
            "scope": "/read-public",
        }
        self.request("POST", params=params, headers=headers, payload=payload)

    def _check_availability(self) -> None:
        pass
