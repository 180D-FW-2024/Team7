"""
ble_central.py

Usage without socket:
$ python central.py 0

Runs in subprocess created in game

Connects to esp32-c6 and receives imu data via ble
"""
import asyncio
from bleak import BleakScanner, BleakClient
from bleak.exc import BleakError
import struct
import socket, time
import sys

# Your UUIDs from the peripheral
IMU_SERVICE_UUID = "1b9998a2-1234-5678-1234-56789abcdef0"
ACCEL_CHAR_UUID = "2713d05a-1234-5678-1234-56789abcdef1"
GYRO_CHAR_UUID = "2713d05b-1234-5678-1234-56789abcdef2"

arg = sys.argv[1]

def connect_with_retry():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client_socket.connect(('localhost', 8080))
            print("Connected to server")
            return client_socket
        except ConnectionRefusedError:
            print("Server not available, retrying in 1 second...")
            time.sleep(1)

if arg != "0":
    print("here")
    client_socket = connect_with_retry()

async def find_imu_peripheral():
    """
    Scan for the IMU_Sensor peripheral and return its device object.
    """
    print("Scanning for IMU_Sensor peripheral...")

    def detection_callback(device, advertising_data):
        # Filter to find IMU_Sensor by name
        return device.name and "IMU_Sensor" in device.name

    try:
        device = await BleakScanner.find_device_by_filter(
            detection_callback,
            timeout=10.0  # Increased timeout to 10 seconds
        )

        if device:
            print(f"Found IMU_Sensor: {device.name} ({device.address})")
        else:
            print("IMU_Sensor not found. Retrying...")

        return device

    except BleakError as e:
        print(f"BLE Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return None


async def connect_and_read_imu(device):
    """
    Connect to the IMU_Sensor peripheral and read data.
    """
    try:
        print(f"Connecting to {device.name} ({device.address})...")
        async with BleakClient(device) as client:
            if client.is_connected:
                print("Connected to IMU_Sensor")

                while True:
                    # Read IMU data
                    try:
                        accel = await client.read_gatt_char(ACCEL_CHAR_UUID)
                        gyro = await client.read_gatt_char(GYRO_CHAR_UUID)

                        # Unpack structs to three floats
                        accel_data = struct.unpack('<fff', accel)
                        gyro_data = struct.unpack('<fff', gyro)

                        print(f"  Accelerometer (mg): X={accel_data[0]:09.3f}, Y={accel_data[1]:09.3f}, Z={accel_data[2]:09.3f}", end="  ")
                        print(f"  Gyroscope (DPS): X={gyro_data[0]:09.3f}, Y={gyro_data[1]:09.3f}, Z={gyro_data[2]:09.3f}")

                        # adding to socket
                        if arg != "0":
                            accel_data = f"{gyro_data[0]},{gyro_data[1]},{gyro_data[2]}"
                            client_socket.send(accel_data.encode())

                        # Wait for the next reading 
                        # Test different values -- try 0.09 
                        await asyncio.sleep(0.06)

                    except BleakError as e:
                        print(f"Error reading IMU data: {e}")
                        break

    except Exception as e:
        print(f"Connection error: {e}")


async def main():
    """
    Main loop to scan and connect to the IMU_Sensor peripheral.
    """
    while True:
        device = await find_imu_peripheral()
        if device:
            await connect_and_read_imu(device)
        else:
            await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped by user")