"""Asynchronous Python client for CentriConnect/MyPropane API."""

from typing import Optional

from aiohttp import ClientSession

from .api import API
from .tank import Tank


class CentriConnect:
    """Main class for reading data for a CentriConnect/MyPropane tank."""

    def __init__(
        self,
        user_id: str,
        device_id: str,
        device_auth: str,
        session: Optional[ClientSession] = None,
        timeout: float = 1,
    ):
        if session is None:
            session = ClientSession()
            self._session = session
        self.api = API(user_id, device_id, device_auth, session, timeout)

    async def async_get_tank_data(self) -> Tank:
        """Get tank data"""
        return Tank(await self.api.async_request())

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_exc_info) -> None:
        if self._session:
            await self._session.close()
