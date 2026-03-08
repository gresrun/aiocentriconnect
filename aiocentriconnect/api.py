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
)


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
    async def async_request(self) -> dict:
        """Make an asynchronous request to the CentriConnect/MyPropane API.
        Args:
            user_id: The ID of the user for which to fetch data
            device_id: The ID of the device for which to fetch data
            device_auth: The device authentication code

        Raises:
            CentriConnectConnectionTimeoutError: The connection timed out
            CentriConnectConnectionError: Any communication error

        Returns:
            Data for the given endpoint
        """
        try:
            async with async_timeout.timeout(self.timeout):
                async with self.session.get(self.build_url()) as response:
                    response.raise_for_status()
                    return await self._decode_response(response)
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

    async def _decode_response(self, response: aiohttp.ClientResponse) -> dict:
        """Decode JSON response."""
        raw_body = await response.text()
        try:
            json_body = json.loads(raw_body)
            if (json_body is None) or (self.device_id not in json_body):
                raise CentriConnectDecodeError(
                    "CentriConnect API response did not contain expected data",
                    raw_body,
                )
            return json_body[self.device_id]
        except JSONDecodeError as ex:
            raise CentriConnectDecodeError(
                "Error decoding JSON response from CentriConnect", raw_body
            ) from ex
