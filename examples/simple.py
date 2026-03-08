""" Simple example showing usage of this library """
# pylint: disable=missing-function-docstring

import asyncio

from aiocentriconnect import CentriConnect


async def main():
    user_id = input("User ID: ")
    device_id = input("Device ID: ")
    device_auth = input("Device auth code: ")

    async with CentriConnect(user_id, device_id, device_auth) as centriconnect:
        tank_data = await centriconnect.async_get_tank_data()
        print(f"'{tank_data.device_name}' is {tank_data.tank_level}% full")


asyncio.run(main())
