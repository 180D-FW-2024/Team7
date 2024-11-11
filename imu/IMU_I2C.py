import utime
import math
from LSM6DSL import *
import machine

# I2C Setup
sda = machine.Pin(0)
scl = machine.Pin(1)
i2c = machine.I2C(0, sda=sda, scl=scl, freq=100000)

def writeReg(reg_address, data):
    try:
        i2c.writeto_mem(LSM6DSL_ADDRESS, reg_address, bytes([data]))
    except Exception as e:
        print(f"Error writing to register {reg_address}: {e}")

def readReg(reg_address):
    try:
        res = i2c.readfrom_mem(LSM6DSL_ADDRESS, reg_address, 1)
        return res
    except Exception as e:
        print(f"Error reading from register {reg_address}: {e}")
        return None

# Reading Accelerometer Data
def readACCx():
    acc_l = readReg(LSM6DSL_OUTX_L_XL)
    acc_h = readReg(LSM6DSL_OUTX_H_XL)
    acc_combined = int.from_bytes(acc_l, 'little') | int.from_bytes(acc_h, 'little') << 8
    return acc_combined if acc_combined < 32768 else acc_combined - 65536

def readACCy():
    acc_l = readReg(LSM6DSL_OUTY_L_XL)
    acc_h = readReg(LSM6DSL_OUTY_H_XL)
    acc_combined = int.from_bytes(acc_l, 'little') | int.from_bytes(acc_h, 'little') << 8
    return acc_combined if acc_combined < 32768 else acc_combined - 65536

def readACCz():
    acc_l = readReg(LSM6DSL_OUTZ_L_XL)
    acc_h = readReg(LSM6DSL_OUTZ_H_XL)
    acc_combined = int.from_bytes(acc_l, 'little') | int.from_bytes(acc_h, 'little') << 8
    return acc_combined if acc_combined < 32768 else acc_combined - 65536

# Reading Gyroscope Data
def readGYRx():
    gyr_l = readReg(LSM6DSL_OUTX_L_G)
    gyr_h = readReg(LSM6DSL_OUTX_H_G)
    gyr_combined = int.from_bytes(gyr_l, 'little') | int.from_bytes(gyr_h, 'little') << 8
    return gyr_combined if gyr_combined < 32768 else gyr_combined - 65536

def readGYRy():
    gyr_l = readReg(LSM6DSL_OUTY_L_G)
    gyr_h = readReg(LSM6DSL_OUTY_H_G)
    gyr_combined = int.from_bytes(gyr_l, 'little') | int.from_bytes(gyr_h, 'little') << 8
    return gyr_combined if gyr_combined < 32768 else gyr_combined - 65536

def readGYRz():
    gyr_l = readReg(LSM6DSL_OUTZ_L_G)
    gyr_h = readReg(LSM6DSL_OUTZ_H_G)
    gyr_combined = int.from_bytes(gyr_l, 'little') | int.from_bytes(gyr_h, 'little') << 8
    return gyr_combined if gyr_combined < 32768 else gyr_combined - 65536

# IMU Initialization
def initIMU():
    device_addresses = i2c.scan()
    print("I2C devices found:", device_addresses)

    if LSM6DSL_ADDRESS not in device_addresses:
        print("Error: BerryIMU not detected on I2C bus")
        return False

    writeReg(LSM6DSL_CTRL1_XL, 0b10011111)  # Accelerometer settings
    writeReg(LSM6DSL_CTRL8_XL, 0b11001000)  # Low-pass filter enabled
    writeReg(LSM6DSL_CTRL3_C, 0b01000100)   # Block Data Update, auto increment
    writeReg(LSM6DSL_CTRL2_G, 0b10011100)   # Gyroscope settings

    print("IMU initialized successfully")
    return True