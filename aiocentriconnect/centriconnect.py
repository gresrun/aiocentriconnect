"""Asynchronous Python client for CentriConnect/MyPropane API."""

from typing import Optional

from aiohttp import ClientSession
from datetime import datetime

from aiocentriconnect.types import TankDict

from .api import API


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

    async def __aexit__(self, *_exc_info) -> None:  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
        if self._session:
            await self._session.close()


class Tank:
    """Data about a CentriConnect/MyPropane tank."""

    def __init__(self, raw_data: TankDict):
        self.raw_data = raw_data

    @property
    def alert_status(self) -> float:
        """Alert status"""
        return self.raw_data["AlertStatus"]

    @property
    def altitude(self) -> float:
        """Altitude"""
        return self.raw_data["Altitude"]

    @property
    def battery_voltage(self) -> float:
        """Battery voltage"""
        return self.raw_data["BatteryVolts"]

    @property
    def device_id(self) -> str:
        """Device ID"""
        return self.raw_data["DeviceID"]

    @property
    def device_name(self) -> str:
        """Device name"""
        return self.raw_data["DeviceName"]

    @property
    def device_temperature(self) -> float:
        """Device temperature"""
        return self.raw_data["DeviceTempFahrenheit"]

    @property
    def last_post_time(self) -> datetime:
        """Last post time"""
        string_time = self.raw_data["LastPostTimeIso"]
        date = string_time.replace(" ", "T") + "Z"
        return datetime.fromisoformat(date)

    @property
    def latitude(self) -> float:
        """Latitude"""
        return self.raw_data["Latitude"]

    @property
    def longitude(self) -> float:
        """Longitude"""
        return self.raw_data["Longitude"]

    @property
    def next_post_time(self) -> datetime:
        """Next post time"""
        string_time = self.raw_data["NextPostTimeIso"]
        date = string_time.replace(" ", "T") + "Z"
        return datetime.fromisoformat(date)

    @property
    def lte_signal_strength(self) -> float:
        """LTE signal strength"""
        return self.raw_data["SignalQualLTE"]

    @property
    def solar_voltage(self) -> float:
        """Solar voltage"""
        return self.raw_data["SolarVolts"]

    @property
    def tank_level(self) -> float:
        """Tank level"""
        return self.raw_data["TankLevel"]

    @property
    def tank_size(self) -> int:
        """Tank size"""
        return self.raw_data["TankSize"]

    @property
    def tank_size_unit(self) -> int:
        """Tank size unit"""
        return self.raw_data["TankSizeUnit"]

    @property
    def hardware_version(self) -> str:
        """Hardware version"""
        return self.raw_data["VersionHW"]

    @property
    def lte_version(self) -> str:
        """LTE version"""
        return self.raw_data["VersionLTE"]
