from imu.i2cbus import I2CBus
from imu.berryimu import BerryIMU
import logging


def test_i2c_scan():
    """
    Test if the I2C bus detects devices correctly.
    """
    i2c_bus = I2CBus()
    devices = i2c_bus.i2c.scan()
    print(f"I2C devices found: {devices}")
    assert len(devices) > 0, "No devices detected on I2C bus."


def test_imu_initialization():
    """
    Test if the IMU initializes correctly.
    """
    i2c_bus = I2CBus()
    assert i2c_bus.initialize_imu(), "IMU initialization failed."


def test_read_sensors():
    """
    Test if the IMU returns valid sensor readings.
    """
    i2c_bus = I2CBus()
    imu = BerryIMU(i2c_bus)
    imu.initialize()
    acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z = imu.read_sensors()
    print(f"Accelerometer: {acc_x}, {acc_y}, {acc_z}")
    print(f"Gyroscope: {gyr_x}, {gyr_y}, {gyr_z}")
    assert (
        acc_x != 0 or acc_y != 0 or acc_z != 0
    ), "Accelerometer readings are all zero."
    assert gyr_x != 0 or gyr_y != 0 or gyr_z != 0, "Gyroscope readings are all zero."
