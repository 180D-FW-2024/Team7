"""
Guide to enable I2C communication on Pico W can be found here:
https://ozzmaker.com/i2c/
"""

from imu.LSM6DSL import *
from utils.config import I2C_SDA_PIN, I2C_SCL_PIN, I2C_FREQ

try:
    import machine  # For MicroPython environment
except ImportError:
    from mock_machine import Pin, I2C  # Use mock classes in local environment


class I2CBus:
    """
    Handles I2C communication with the BerryIMU.
    """

    def __init__(self):
        """
        Initializes the I2C bus with specified pins and frequency.
        """
        self.i2c = machine.I2C(0, sda=machine.Pin(I2C_SDA_PIN), scl=machine.Pin(I2C_SCL_PIN), freq=I2C_FREQ)

    def write_register(self, register, data):
        """
        Writes a byte to a specified register.
        :param register: Register address.
        :param data: Data to write.
        """
        self.i2c.writeto_mem(LSM6DSL_ADDRESS, register, bytes([data]))

    def read_register(self, register, length=1):
        """
        Reads data from a specified register.
        :param register: Register address.
        :param length: Number of bytes to read.
        :return: Byte data.
        """
        return self.i2c.readfrom_mem(LSM6DSL_ADDRESS, register, length)

    def read_combined(self, low_addr, high_addr):
        """
        Reads and combines low and high byte registers into a 16-bit signed value.
        :param low_addr: Address of the low byte register.
        :param high_addr: Address of the high byte register.
        :return: Signed 16-bit value.
        """
        low = int.from_bytes(self.read_register(low_addr), "little")
        high = int.from_bytes(self.read_register(high_addr), "little") << 8
        value = low | high
        return value if value < 32768 else value - 65536

    def read_acc_x(self):
        """Reads the X-axis value from the accelerometer."""
        return self.read_combined(LSM6DSL_OUTX_L_XL, LSM6DSL_OUTX_H_XL)

    def read_acc_y(self):
        """Reads the Y-axis value from the accelerometer."""
        return self.read_combined(LSM6DSL_OUTY_L_XL, LSM6DSL_OUTY_H_XL)

    def read_acc_z(self):
        """Reads the Z-axis value from the accelerometer."""
        return self.read_combined(LSM6DSL_OUTZ_L_XL, LSM6DSL_OUTZ_H_XL)

    def read_gyro_x(self):
        """Reads the X-axis value from the gyroscope."""
        return self.read_combined(LSM6DSL_OUTX_L_G, LSM6DSL_OUTX_H_G)

    def read_gyro_y(self):
        """Reads the Y-axis value from the gyroscope."""
        return self.read_combined(LSM6DSL_OUTY_L_G, LSM6DSL_OUTY_H_G)

    def read_gyro_z(self):
        """Reads the Z-axis value from the gyroscope."""
        return self.read_combined(LSM6DSL_OUTZ_L_G, LSM6DSL_OUTZ_H_G)

    def initialize_imu(self):
        """
        Configures IMU registers for operation.
        :return: True if the IMU is detected and initialized successfully, False otherwise.
        """
        if LSM6DSL_ADDRESS not in self.i2c.scan():
            print("Error: IMU not detected.")
            return False

        # Configure accelerometer
        self.write_register(LSM6DSL_CTRL1_XL, 0b10011111)
        self.write_register(LSM6DSL_CTRL8_XL, 0b11001000)

        # Configure gyroscope
        self.write_register(LSM6DSL_CTRL2_G, 0b10011100)

        # Common settings
        self.write_register(LSM6DSL_CTRL3_C, 0b01000100)

        print("IMU initialized successfully.")
        return True