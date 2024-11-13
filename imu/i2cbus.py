"""
Guide to enable I2C communication on Pico W can be found here:
https://ozzmaker.com/i2c/
"""

# Uncomment when sing actual hardware
import machine
from LSM6DSL import *

# I2C Setup
sda = machine.Pin(0)
scl = machine.Pin(1)
i2c = machine.I2C(0, sda=sda, scl=scl, freq=100000)


def write_register(register_address, data):
    res = bytearra(2)
    i2c.writeto_mem(LSM6DSL_ADDRESS, register, bytes([data]))


def read_register(register):
    return i2c.readfrom_mem(LSM6DSL_ADDRESS, register, 1)


def readACCx():
    acc_l = readReg(LSM6DSL_OUTX_L_XL)
    acc_h = readReg(LSM6DSL_OUTX_H_XL)
    acc_combined = (
        ord(acc_l) | ord(acc_h) << 8
    )  # ord is to get int representation from a byte
    return acc_combined if acc_combined < 32768 else acc_combined - 65536


def readACCy():
    acc_l = readReg(LSM6DSL_OUTY_L_XL)
    acc_h = readReg(LSM6DSL_OUTY_H_XL)
    acc_combined = (
        ord(acc_l) | ord(acc_h) << 8
    )  # ord is to get int representation from a byte
    return acc_combined if acc_combined < 32768 else acc_combined - 65536


def readACCz():
    acc_l = readReg(LSM6DSL_OUTZ_L_XL)
    acc_h = readReg(LSM6DSL_OUTZ_H_XL)
    acc_combined = (
        ord(acc_l) | ord(acc_h) << 8
    )  # ord is to get int representation from a byte
    return acc_combined if acc_combined < 32768 else acc_combined - 65536


def readGYRx():
    gyr_l = readReg(LSM6DSL_OUTX_L_G)
    gyr_h = readReg(LSM6DSL_OUTX_H_G)
    gyr_combined = (
        ord(gyr_l) | ord(gyr_h) << 8
    )  # ord is to get int representation from a byte
    return gyr_combined if gyr_combined < 32768 else gyr_combined - 65536


def readGYRy():
    gyr_l = readReg(LSM6DSL_OUTY_L_G)
    gyr_h = readReg(LSM6DSL_OUTY_H_G)
    gyr_combined = (
        ord(gyr_l) | ord(gyr_h) << 8
    )  # ord is to get int representation from a byte
    return gyr_combined if gyr_combined < 32768 else gyr_combined - 65536


def readGYRz():
    gyr_l = readReg(LSM6DSL_OUTZ_L_G)
    gyr_h = readReg(LSM6DSL_OUTZ_H_G)
    gyr_combined = (
        ord(gyr_l) | ord(gyr_h) << 8
    )  # ord is to get int representation from a byte
    return gyr_combined if gyr_combined < 32768 else gyr_combined - 65536


def initialize_imu():
    if LSM6DSL_ADDRESS not in i2c.scan():
        print("Error: IMU not detected")
        return False

    # Configure accelerometer and gyroscope

    writeReg(LSM6DSL_CTRL1_XL, 0b10011111)  # ODR 3.33 kHz, +/- 8g , BW = 400hz
    writeReg(
        LSM6DSL_CTRL8_XL, 0b11001000
    )  # Low pass filter enabled, BW9, composite filter
    writeReg(
        LSM6DSL_CTRL3_C, 0b01000100
    )  # Enable Block Data update, increment during multi byte read

    writeReg(LSM6DSL_CTRL2_G, 0b10011100)  # ODR 3.3 kHz, 2000 dps

    print("IMU initialized successfully")
    return True
