
# This serves as client-side code to interface with BLE peripheral
# Code inspiration from https://github.com/hbldh/bleak/discussions/1261


from bleak import BleakClient, BleakScanner
import asyncio
from datetime import datetime
import struct


# ADDRESS = "28:cd:c1:08:6b:9d"
# ACCEL_UUID = "08a7bf2a-5676-4c4e-9611-e572864d294f"
# GYRO_UUID = "49fffa93-076f-44cd-997d-4f145bad5a5c"

ACCEL_UUID = '2713d05a-1234-5678-1234-56789abcdef1'
GYRO_UUID = '2713d05b-1234-5678-1234-56789abcdef2'


# find ble device based on name "pico"
async def find_device():
    # name = "pico"
    name = "IMU_Sensor"
    return await BleakScanner.find_device_by_name(name)


# handler for gyroscope notifications
global gyro_byte_buffer; gyro_byte_buffer = []
def gyro_handler(characteristic, data):
    current_timestamp_entry = datetime.now()
    list_entry = (str(current_timestamp_entry) + "; " + data.hex())
    gyro_byte_buffer.append(list_entry)

    # print values
    [ts, val] = list_entry.split("; ")
    val = bytes.fromhex(val)
    [gyro_x, gyro_y, gyro_z] = struct.unpack('<hhh', val)
    print(f"Gyro x: {gyro_x}, y: {gyro_y}, z: {gyro_z}")


# handler for accelerometer notifications
global accel_byte_buffer; accel_byte_buffer = []
def accel_handler(characteristic, data):
    current_timestamp_entry = datetime.now()
    list_entry = (str(current_timestamp_entry) + "; " + data.hex())
    accel_byte_buffer.append(list_entry)

    # print values
    [ts, val] = list_entry.split("; ")
    val = bytes.fromhex(val)
    [accel_x, accel_y, accel_z] = struct.unpack('<hhh', val)
    print(f"Accel x: {accel_x}, y: {accel_y}, z: {accel_z}")


# collect IMU data from peripheral device via BLE
async def collect_data(gyro_uuid, accel_uuid):

    # connect
    print("Start scanning for device")
    device = await find_device()
    if not device:
        print("Device not found")
        return

    # while connected and notifications enabled, read data
    async with BleakClient(device) as client:
        print(f"Connected: {client.is_connected}")
        await client.start_notify(gyro_uuid, gyro_handler)
        await client.start_notify(accel_uuid, accel_handler)
        print("Notifications enabled... Reading data")
        await asyncio.sleep(15.0)
        await client.stop_notify(gyro_uuid)
        await client.stop_notify(accel_uuid)
        print("Reading complete")


if __name__ == "__main__":

    asyncio.run(collect_data(GYRO_UUID, ACCEL_UUID))



