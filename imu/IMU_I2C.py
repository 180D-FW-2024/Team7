# Uncomment when sing actual hardware
# import machine
# from imu.LSM6DSL import *

# Mocked I2C setup, (Actual would use machine.Pin and machine.I2C)
# I2C Setup
# sda = machine.Pin(0)
# scl = machine.Pin(1)
# i2c = machine.I2C(0, sda=sda, scl=scl, freq=100000)


def initialize_imu():
    """
    Mock initialization of the IMU.
    Simulates checking the I2C bus for the BerryIMU address and configuring
    the accelerometer and gyroscope. For real hardware, uncomment the
    machine.Pin and i2c setup sections.

    Returns:
        bool: True if the IMU is detected and initialized, False otherwise.
    """
    # Assuming 0x6A as IMU mock address
    device_addresses = [0x6A]  # Mock detected address list
    if LSM6DSL_ADDRESS not in device_addresses:
        print("Error: IMU not detected")
        return False

    print("IMU initialized successfully")
    return True


import random


# Mocked function for data reading when IMU is not conencted
def read_accel_data():
    """
    Simulates accelerometer data by returning random values within a specified range.
    Useful for testing data flow and processing without real hardware.

    Returns:
        dict: Mocked accelerometer readings for x, y, and z axes.
    """
    return {
        "x": random.randint(-16000, 16000),
        "y": random.randint(-16000, 16000),
        "z": random.randint(-16000, 16000),
    }


def read_gyro_data():
    """
    Simulates gyroscope data by returning random values within a specified range.
    Useful for testing data flow and processing without real hardware.

    Returns:
        dict: Mocked gyroscope readings for x, y, and z axes.
    """
    return {
        "x": random.randint(-250, 250),
        "y": random.randint(-250, 250),
        "z": random.randint(-250, 250),
    }


"""
def initialize_imu():
    if LSM6DSL_ADDRESS not in i2c.scan():
        print("Error: IMU not detected")
        return False

    Configure accelerometer and gyroscope
    
    #Change register values for desired sensitivity and output rate
    
    write_register(LSM6DSL_CTRL1_XL, 0b10011111)  # Accelerometer settings
    write_register(LSM6DSL_CTRL2_G, 0b10011100)   # Gyroscope settings
    print("IMU initialized successfully")
    return True

def write_register(register, data):
    i2c.writeto_mem(LSM6DSL_ADDRESS, register, bytes([data]))

def read_register(register):
    return i2c.readfrom_mem(LSM6DSL_ADDRESS, register, 1)

def read_accel_data():
    # Read and combine accelerometer data for each axis
    return {
        'x': int.from_bytes(read_register(LSM6DSL_OUTX_L_XL) + read_register(LSM6DSL_OUTX_H_XL), 'little', signed=True),
        'y': int.from_bytes(read_register(LSM6DSL_OUTY_L_XL) + read_register(LSM6DSL_OUTY_H_XL), 'little', signed=True),
        'z': int.from_bytes(read_register(LSM6DSL_OUTZ_L_XL) + read_register(LSM6DSL_OUTZ_H_XL), 'little', signed=True)
    }

def read_gyro_data():
    # Read and combine gyroscope data for each axis
    return {
        'x': int.from_bytes(read_register(LSM6DSL_OUTX_L_G) + read_register(LSM6DSL_OUTX_H_G), 'little', signed=True),
        'y': int.from_bytes(read_register(LSM6DSL_OUTY_L_G) + read_register(LSM6DSL_OUTY_H_G), 'little', signed=True),
        'z': int.from_bytes(read_register(LSM6DSL_OUTZ_L_G) + read_register(LSM6DSL_OUTZ_H_G), 'little', signed=True)
    }
"""
