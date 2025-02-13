# This is micropython code meant to serve as BLE peripheral device
# Code inspiration from https://coffeebreakpoint.com/micropython/raspberry-pi-pico-w-bluetooth/

import sys

sys.path.append("")

from micropython import const
import uasyncio as asyncio
import aioble
import bluetooth
import struct
import random


# Tunable params:
DATA_POLLING_PERIOD_MS = 10
DATA_TRANSMIT_PERIOD_MS = 10


# BLE uuids
_IMU_UUID = bluetooth.UUID("3762268c-690f-43cd-bf48-0c1afd892f71")
_ACCEL_UUID = bluetooth.UUID("08a7bf2a-5676-4c4e-9611-e572864d294f")
_GYRO_UUID = bluetooth.UUID("49fffa93-076f-44cd-997d-4f145bad5a5c")
_ADV_APPEARANCE_GENERIC_SENSOR = const(1344)

# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250_000


# Register GATT server.
imu_service = aioble.Service(_IMU_UUID)
accel_characteristic = aioble.Characteristic(
    imu_service, _ACCEL_UUID, read=True, notify=True
)
gyro_characteristic = aioble.Characteristic(
    imu_service, _GYRO_UUID, read=True, notify=True
)
aioble.register_services(imu_service)


# Helpers to encode characteristics (sint16)
def _encode_accel(acceleration):
    return struct.pack("<hhh", *tuple(int(axis) for axis in acceleration))


def _encode_gyro(angular_velocity):
    return struct.pack("<hhh", *tuple(int(axis) for axis in angular_velocity))


# randomize sensor data
def random_value():
    x = random.uniform(-100, 100)
    y = random.uniform(-100, 100)
    z = random.uniform(-100, 100)
    return (x, y, z)


# periodically poll the IMU
async def sensor_task():
    acceleration = (1, 1, 1)
    angular_velocity = (2, 2, 2)
    while True:
        accel_characteristic.write(_encode_accel(acceleration))
        gyro_characteristic.write(_encode_gyro(angular_velocity))
        await asyncio.sleep_ms(DATA_POLLING_PERIOD_MS)


# send updated value of the characteristic to client over established connection
async def notify_gatt_client(connection):
    if connection is None:
        return
    accel_characteristic.notify(connection)
    gyro_characteristic.notify(connection)


# serially wait for connections -- do not advertise while a central is connected
async def peripheral_task():
    while True:
        async with await aioble.advertise(
            _ADV_INTERVAL_MS,
            name="pico",
            services=[_IMU_UUID],
            appearance=_ADV_APPEARANCE_GENERIC_SENSOR,
        ) as connection:
            print("Connection from", connection.device)
            while connection.is_connected():
                await notify_gatt_client(connection)
                await asyncio.sleep_ms(DATA_TRANSMIT_PERIOD_MS)


# Run both tasks.
async def main():
    t1 = asyncio.create_task(sensor_task())
    t2 = asyncio.create_task(peripheral_task())
    await asyncio.gather(t1, t2)


asyncio.run(main())
