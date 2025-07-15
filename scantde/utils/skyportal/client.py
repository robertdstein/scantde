"""
Basic SkyPortal API client.
"""

import logging
import os
from typing import Mapping, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

DEFAULT_TIMEOUT = 60  # seconds
SKYPORTAL_ORIGIN = "tdescore"

logger = logging.getLogger(__name__)

class NoCredentialsError(KeyError):
    """
    Exception raised when no credentials are provided.
    """


class TimeoutHTTPAdapter(HTTPAdapter):
    """
    HTTP adapter that sets a default timeout for all requests.
    """

    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, *args, **kwargs):
        """
        Send a request with a default timeout.

        :param request: request to send
        :param args: args to pass to super().send
        :param kwargs: kwargs to pass to super().send
        :return: response from request
        """
        try:
            timeout = kwargs.get("timeout")
            if timeout is None:
                kwargs["timeout"] = self.timeout
            return super().send(request, *args, **kwargs)
        except AttributeError:
            kwargs["timeout"] = DEFAULT_TIMEOUT


class SkyportalClient:
    """
    Basic Skyportal client class for executing functions
    """

    def __init__(
        self,
        base_url: str = "https://fritz.science/api/",
    ):
        self.base_url = base_url
        self._session = None
        self.session_headers = None

    def set_up_session(self):
        """
        Set up a session for sending requests to Skyportal.

        :return: None
        """
        # session to talk to SkyPortal
        self._session = requests.Session()
        self.session_headers = {
            "Authorization": f"token {self._get_fritz_token()}",
            "User-Agent": "mirar",
        }

        retries = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[405, 429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "POST", "PATCH"],
        )
        adapter = TimeoutHTTPAdapter(max_retries=retries)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def get_session(self) -> requests.Session:
        """
        Wrapper for getting the session.
        If the session is not set up, it will be set up.

        :return: Session
        """
        if self._session is None:
            self.set_up_session()

        return self._session

    @staticmethod
    def _get_fritz_token() -> str:
        """
        Get Fritz token from environment variable.

        :return: Fritz token
        """
        skyportal_token = os.getenv("SKYPORTAL_TOKEN")
        if skyportal_token is None:
            err = ("No Skyportal token specified. "
                   "Add this to .env or set SKYPORTAL_TOKEN environment variable.")
            logger.error(err)
            raise NoCredentialsError(err)

        return skyportal_token

    def api(
        self, method: str, endpoint: str, data: Optional[Mapping] = None
    ) -> requests.Response:
        """Make an API call to a SkyPortal instance

        headers = {'Authorization': f'token {self.token}'}
        response = requests.request(method, endpoint, json_dict=data, headers=headers)

        :param method: HTTP method
        :param endpoint: API endpoint
        :param data: JSON data to send
        :return: response from API call
        """
        method = method.lower()

        session = self.get_session()

        methods = {
            "head": session.head,
            "get": session.get,
            "post": session.post,
            "put": session.put,
            "patch": session.patch,
            "delete": session.delete,
        }

        if endpoint is None:
            raise ValueError("Endpoint not specified")
        if method not in ["head", "get", "post", "put", "patch", "delete"]:
            raise ValueError(f"Unsupported method: {method}")

        url = urljoin(self.base_url, endpoint)

        if method == "get":
            response = methods[method](
                url,
                params=data,
                headers=self.session_headers,
            )
        else:
            response = methods[method](
                url,
                json=data,
                headers=self.session_headers,
            )

        return response
