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

enable_print = False
if len(sys.argv) > 1 and "-p" in sys.argv:
    enable_print = True 

run_with_socket = True
if len(sys.argv) > 1 and sys.argv[1] == "0":
    run_with_socket = False

def connect_with_retry():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client_socket.connect(('localhost', 8080))
            if enable_print: print("Connected to server")
            return client_socket
        except ConnectionRefusedError:
            if enable_print: print("Server not available, retrying in 1 second...")
            time.sleep(1)

if run_with_socket:
    # print("here")
    client_socket = connect_with_retry()

async def find_imu_peripheral():
    """
    Scan for the IMU_Sensor peripheral and return its device object.
    """
    if enable_print: print("Scanning for IMU_Sensor peripheral...")

    def detection_callback(device, advertising_data):
        # Filter to find IMU_Sensor by name
        return device.name and "IMU_Sensor" in device.name

    try:
        device = await BleakScanner.find_device_by_filter(
            detection_callback,
            timeout=10.0  # Increased timeout to 10 seconds
        )

        if device:
            if enable_print: print(f"Found IMU_Sensor: {device.name} ({device.address})")
        else:
            if enable_print: print("IMU_Sensor not found. Retrying...")

        return device

    except BleakError as e:
        if enable_print: print(f"BLE Error: {e}")
    except Exception as e:
        if enable_print: print(f"Unexpected error: {e}")

    return None


async def connect_and_read_imu(device):
    """
    Connect to the IMU_Sensor peripheral and read data.
    """
    try:
        if enable_print: print(f"Connecting to {device.name} ({device.address})...")
        async with BleakClient(device) as client:
            if client.is_connected:
                if enable_print: print("Connected to IMU_Sensor")

                while True:
                    # Read IMU data
                    try:
                        accel = await client.read_gatt_char(ACCEL_CHAR_UUID)
                        gyro = await client.read_gatt_char(GYRO_CHAR_UUID)

                        # Unpack structs to three floats
                        accel_data = struct.unpack('<fff', accel)
                        gyro_data = struct.unpack('<fff', gyro)

                        # accel_z_normalized = accel_data[2] - 992.00

                        if enable_print: print(f"  Accelerometer (mg): X={accel_data[0]:09.3f}, Y={accel_data[1]:09.3f}, Z={accel_data[2]:09.3f}", end="  ")
                        if enable_print: print(f"  Gyroscope (DPS): X={gyro_data[0]:09.3f}, Y={gyro_data[1]:09.3f}, Z={gyro_data[2]:09.3f}")

                        # adding to socket
                        if run_with_socket:
                            data = f"{gyro_data[0]},{gyro_data[1]},{gyro_data[2]}"
                            client_socket.send(data.encode())

                        # Wait for the next reading 
                        # Test different values -- try 0.09 
                        await asyncio.sleep(0.06)

                    except BleakError as e:
                        if enable_print: print(f"Error reading IMU data: {e}")
                        break

    except Exception as e:
        if enable_print: print(f"Connection error: {e}")


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
        if enable_print: print("\nStopped by user")