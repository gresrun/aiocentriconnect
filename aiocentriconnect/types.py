"""Inner types for CentriConnect/MyPropane API."""

from typing import TypedDict


class TankDict(TypedDict):
    """Typed dictionary for a CentriConnect/MyPropane tank."""

    AlertStatus: str
    Altitude: float
    BatteryVolts: float
    DeviceID: str
    DeviceName: str
    DeviceTempFahrenheit: float
    LastPostTimeIso: str
    Latitude: float
    Longitude: float
    NextPostTimeIso: str
    SignalQualLTE: float
    SolarVolts: float
    TankLevel: float
    TankSize: int
    TankSizeUnit: str
    VersionHW: str
    VersionLTE: str
