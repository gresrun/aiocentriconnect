"""Tests for CentriConnect/MyPropane API"""
# pylint: disable=missing-function-docstring

import asyncio

import aiohttp
from aiohttp.web import Response
import pytest

from aiocentriconnect import CentriConnect
from aiocentriconnect.exceptions import (
    CentriConnectConnectionError,
    CentriConnectConnectionTimeoutError,
    CentriConnectDecodeError,
    CentriConnectNotFoundError,
    CentriConnectTooManyRequestsError,
)
from aresponses.main import ResponsesMockServer  # type: ignore

fake_user_id = "12345678-9012-3456-7a89-b012345cde6f"
fake_device_id = "123a4b5c-678d-9e0f-a123-4b567c8d901e"
fake_device_auth = "123456"
fake_response = """
{
    "123a4b5c-678d-9e0f-a123-4b567c8d901e": {
        "AlertStatus": "No Alert",
        "Altitude": 123.456,
        "BatteryVolts": 4.19,
        "DeviceID": "123a4b5c-678d-9e0f-a123-4b567c8d901e",
        "DeviceName": "My Tank",
        "DeviceTempCelsius": 17.0,
        "DeviceTempFahrenheit": 63.0,
        "LastPostTimeIso": "2026-02-27 22:00:31.000",
        "Latitude": 40.7128,
        "Longitude": -74.0060,
        "NextPostTimeIso": "2026-02-28 10:00:00.000",
        "SignalQualLTE": -107.0,
        "SolarVolts": 2.46,
        "TankLevel": 75.0,
        "TankSize": 1000,
        "TankSizeUnit": "Gallons",
        "VersionHW": "4.1",
        "VersionLTE": "1.1.2"
    }
}
"""
api_host = "api.centriconnect.com"
api_path = (
    f"/centriconnect/{fake_user_id}/device/{fake_device_id}"
    + f"/all-data?device_auth={fake_device_auth}"
)


@pytest.mark.asyncio
async def test_tank_data_request(aresponses: ResponsesMockServer):
    add_valid_tank_data_response(aresponses)

    async with aiohttp.ClientSession() as session:
        centriconnect = CentriConnect(
            fake_user_id, fake_device_id, fake_device_auth, session=session
        )
        tank_data = await centriconnect.async_get_tank_data()
        assert tank_data.alert_status == "No Alert"
        assert tank_data.altitude == 123.456
        assert tank_data.battery_voltage == 4.19
        assert tank_data.device_id == fake_device_id
        assert tank_data.device_name == "My Tank"
        assert tank_data.device_temperature == 63.0
        assert tank_data.latitude == 40.7128
        assert tank_data.longitude == -74.0060
        assert tank_data.last_post_time.isoformat() == "2026-02-27T22:00:31+00:00"
        assert tank_data.next_post_time.isoformat() == "2026-02-28T10:00:00+00:00"
        assert tank_data.lte_signal_strength == -107.0
        assert tank_data.solar_voltage == 2.46
        assert tank_data.tank_level == 75.0
        assert tank_data.tank_size == 1000.0
        assert tank_data.tank_size_unit == "Gallons"
        assert tank_data.hardware_version == "4.1"
        assert tank_data.lte_version == "1.1.2"

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_internal_session(aresponses: ResponsesMockServer):
    add_valid_tank_data_response(aresponses)

    async with CentriConnect(
        fake_user_id, fake_device_id, fake_device_auth
    ) as centriconnect:
        tank_data = await centriconnect.async_get_tank_data()
        assert tank_data.alert_status == "No Alert"

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_timeout(aresponses: ResponsesMockServer):
    async def response_handler(_):
        await asyncio.sleep(0.2)
        return get_valid_tank_data_response(aresponses)

    # Backoff will try 3 times
    for _ in range(3):
        aresponses.add(  # type: ignore
            api_host,  # type: ignore
            api_path,  # type: ignore
            "GET",  # type: ignore
            response_handler,  # type: ignore
            match_querystring=True,
        )

    async with aiohttp.ClientSession() as session:
        centriconnect = CentriConnect(
            fake_user_id, fake_device_id, fake_device_auth, timeout=0.1, session=session
        )
        with pytest.raises(CentriConnectConnectionTimeoutError):
            assert await centriconnect.async_get_tank_data()

    aresponses.assert_plan_strictly_followed()


@pytest.mark.asyncio
async def test_weird_error_response(aresponses: ResponsesMockServer):
    aresponses.add(  # type: ignore
        api_host,  # type: ignore
        api_path,  # type: ignore
        "GET",  # type: ignore
        aresponses.Response(
            status=500, headers={"Content-Type": "text/plain"}, text="Error"
        ),  # type: ignore
        match_querystring=True,
    )

    async with aiohttp.ClientSession() as session:
        centriconnect = CentriConnect(
            fake_user_id, fake_device_id, fake_device_auth, session=session
        )
        with pytest.raises(CentriConnectConnectionError):
            assert await centriconnect.async_get_tank_data()


@pytest.mark.asyncio
async def test_not_found_error_response(aresponses: ResponsesMockServer):
    aresponses.add(  # type: ignore
        api_host,  # type: ignore
        api_path,  # type: ignore
        "GET",  # type: ignore
        aresponses.Response(
            status=404,
            headers={"Content-Type": "text/plain"},
            text='{"error": "NotFound", "message": "Device does not exist."}',
        ),  # type: ignore
        match_querystring=True,
    )

    async with aiohttp.ClientSession() as session:
        centriconnect = CentriConnect(
            fake_user_id, fake_device_id, fake_device_auth, session=session
        )
        with pytest.raises(CentriConnectNotFoundError):
            assert await centriconnect.async_get_tank_data()


@pytest.mark.asyncio
async def test_not_too_many_requests_response(aresponses: ResponsesMockServer):
    aresponses.add(  # type: ignore
        api_host,  # type: ignore
        api_path,  # type: ignore
        "GET",  # type: ignore
        aresponses.Response(
            status=429,
            headers={"Content-Type": "text/plain"},
            text="",
        ),  # type: ignore
        match_querystring=True,
    )

    async with aiohttp.ClientSession() as session:
        centriconnect = CentriConnect(
            fake_user_id, fake_device_id, fake_device_auth, session=session
        )
        with pytest.raises(CentriConnectTooManyRequestsError):
            assert await centriconnect.async_get_tank_data()


@pytest.mark.asyncio
async def test_can_get_raw_response_from_exception(aresponses: ResponsesMockServer):
    malformed_json = """
    {
        "123a4b5c-678d-9e0f-a123-4b567c8d901e": {
            "AlertStatus": "No Alert",
            "Altitude": 123.456,
            "BatteryVolts": 4.19,
    """
    aresponses.add(  # type: ignore
        api_host,  # type: ignore
        api_path,  # type: ignore
        "GET",  # type: ignore
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=malformed_json,
        ),  # type: ignore
        match_querystring=True,
    )

    async with aiohttp.ClientSession() as session:
        centriconnect = CentriConnect(
            fake_user_id, fake_device_id, fake_device_auth, session=session
        )
        try:
            await centriconnect.async_get_tank_data()
        except CentriConnectDecodeError as ex:
            assert ex.get_raw_body() == malformed_json

    aresponses.assert_plan_strictly_followed()


def add_valid_tank_data_response(aresponses: ResponsesMockServer) -> None:
    aresponses.add(  # type: ignore
        api_host,  # type: ignore
        api_path,  # type: ignore
        "GET",  # type: ignore
        get_valid_tank_data_response(aresponses),  # type: ignore
        match_querystring=True,
    )


def get_valid_tank_data_response(
    aresponses: ResponsesMockServer,
) -> Response:
    return aresponses.Response(
        status=200,
        headers={"Content-Type": "application/json"},
        text=fake_response,
    )
