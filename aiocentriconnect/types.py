"""Inner types for CentriConnect/MyPropane API."""

from typing import TypedDict


class TankDict(TypedDict):
    """Typed dictionary for a CentriConnect/MyPropane tank."""

    AlertStatus: float
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
    TankSizeUnit: int
    VersionHW: str
    VersionLTE: str
