"""Data class for CentriConnect/MyPropane Tank information."""

from datetime import datetime

from aiocentriconnect.types import TankDict


class Tank:
    """Object holding information about a CentriConnect/MyPropane tank."""

    def __init__(self, raw_data: TankDict):
        self.raw_data = raw_data

    @property
    def alert_status(self) -> str:
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
    def tank_size_unit(self) -> str:
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
