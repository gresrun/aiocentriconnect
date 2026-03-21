"""CentriConnect/MyPropane API class"""

import asyncio
import json
import socket
from json.decoder import JSONDecodeError

import aiohttp
import async_timeout
import backoff

from .exceptions import (
    CentriConnectConnectionError,
    CentriConnectConnectionTimeoutError,
    CentriConnectDecodeError,
    CentriConnectEmptyResponseError,
    CentriConnectNotFoundError,
    CentriConnectTooManyRequestsError,
)
from .types import TankDict


class API:
    """This class reads data from the CentriConnect/MyPropane API."""

    def __init__(
        self,
        user_id: str,
        device_id: str,
        device_auth: str,
        session: aiohttp.ClientSession,
        timeout: float = 2,
    ):
        self.session = session
        self.timeout = timeout
        self.user_id = user_id
        self.device_id = device_id
        self.device_auth = device_auth

    @backoff.on_exception(
        backoff.expo,
        (CentriConnectConnectionTimeoutError, CentriConnectConnectionError),
        max_tries=3,
    )
    async def async_request(self) -> TankDict:
        """Make an asynchronous request to the CentriConnect/MyPropane API.
        Raises:
            CentriConnectConnectionTimeoutError: The connection timed out
            CentriConnectConnectionError: Any communication error
            CentriConnectNotFoundError: The requested device was not found
            CentriConnectTooManyRequestsError: Too many requests were made to the API
            CentriConnectDecodeError: The API response could not be decoded
            CentriConnectEmptyResponseError: The API response did not contain any data

        Returns:
            Typed dictionary containing the tank data
        """
        try:
            async with async_timeout.timeout(self.timeout):
                async with self.session.get(self.build_url()) as response:
                    return await self._handle_response(response)
        except asyncio.TimeoutError as ex:
            raise CentriConnectConnectionTimeoutError(
                "Timeout while connecting to CentriConnect API"
            ) from ex
        except (aiohttp.ClientError, socket.gaierror) as ex:
            raise CentriConnectConnectionError(
                f"Error while communicating with CentriConnect API: {ex}"
            ) from ex

    def build_url(self) -> str:
        """Construct the URL for a specified user and device."""
        return (
            f"https://api.centriconnect.com/centriconnect/{self.user_id}"
            + f"/device/{self.device_id}/all-data"
            + f"?device_auth={self.device_auth}"
        )

    async def _handle_response(self, response: aiohttp.ClientResponse) -> TankDict:
        """Handle the API response."""
        if response.status == 404:
            raise CentriConnectNotFoundError()
        if response.status == 429:
            raise CentriConnectTooManyRequestsError()
        if not response.ok:
            raise CentriConnectConnectionError(
                f"Received unexpected status code {response.status} from CentriConnect API"
            )
        raw_body = await response.text()
        try:
            json_body = json.loads(raw_body)
            if json_body is None:
                raise CentriConnectEmptyResponseError(
                    "CentriConnect API response did not contain expected data", raw_body
                )
            if "error" in json_body:
                error_msg = json_body["error"]
                if error_msg == "NotFound":
                    raise CentriConnectNotFoundError()
                else:
                    raise CentriConnectDecodeError(
                        "CentriConnect API response did not contain expected data",
                        raw_body,
                    )
            if self.device_id not in json_body:
                raise CentriConnectDecodeError(
                    "CentriConnect API response did not contain expected data",
                    raw_body,
                )
            return json_body[self.device_id]
        except JSONDecodeError as ex:
            raise CentriConnectDecodeError(
                "Error decoding JSON response from CentriConnect", raw_body
            ) from ex
