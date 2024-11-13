"""
Guide to enable I2C communication on Pico W can be found here:
https://ozzmaker.com/i2c/
"""

from imu.LSM6DSL import *
from utils.config import I2C_SDA_PIN, I2C_SCL_PIN, I2C_FREQ
import logging
import machine

class I2CBus:
    """
    Handles I2C communication with the BerryIMU.
    """

    def __init__(self, simulate=False):
        """
        Initializes the I2C bus with specified pins and frequency.
        :param simulate: Whether to run in simulation mode (for local testing).
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.simulate = simulate

        if self.simulate:
            self.logger.info("Simulating I2C bus (no actual hardware).")
            self.i2c = I2C()
        else:
            try:
                self.i2c = machine.I2C(0, sda=machine.Pin(I2C_SDA_PIN), scl=machine.Pin(I2C_SCL_PIN), freq=I2C_FREQ)
                self.logger.info("I2C bus initialized successfully.")
            except Exception as e:
                self.logger.exception(f"Failed to initialize I2C: {e}")
                raise

    def write_register(self, register, data):
        """
        Writes a byte to a specified register.
        :param register: Register address.
        :param data: Data to write.
        """
        try:
            self.i2c.writeto_mem(LSM6DSL_ADDRESS, register, bytes([data]))
            self.logger.debug(f"Write: Address={LSM6DSL_ADDRESS}, Register={register}, Data={data}")
        except Exception as e:
            self.logger.exception(f"Failed to write to register {register}: {e}")

    def read_register(self, register, length=1):
        """
        Reads data from a specified register.
        :param register: Register address.
        :param length: Number of bytes to read.
        :return: Byte data.
        """
        try:
            data = self.i2c.readfrom_mem(LSM6DSL_ADDRESS, register, length)
            self.logger.debug(f"Read: Address={LSM6DSL_ADDRESS}, Register={register}, Data={data}")
            return data
        except Exception as e:
            self.logger.exception(f"Failed to read from register {register}: {e}")
            return b'\x00' * length  # Return default value to avoid crashes

    def read_combined(self, low_addr, high_addr):
        """
        Reads and combines low and high byte registers into a 16-bit signed value.
        :param low_addr: Address of the low byte register.
        :param high_addr: Address of the high byte register.
        :return: Signed 16-bit value.
        """
        try:
            low = int.from_bytes(self.read_register(low_addr), "little")
            high = int.from_bytes(self.read_register(high_addr), "little") << 8
            value = low | high
            return value if value < 32768 else value - 65536
        except Exception as e:
            self.logger.exception(f"Failed to read combined value from {low_addr} and {high_addr}: {e}")
            return 0  # Default value in case of error

    def read_acc(self, axis):
        """
        Reads accelerometer data for a specific axis.
        :param axis: Axis identifier ('x', 'y', or 'z').
        :return: Accelerometer value for the specified axis.
        """
        addr_map = {
            "x": (LSM6DSL_OUTX_L_XL, LSM6DSL_OUTX_H_XL),
            "y": (LSM6DSL_OUTY_L_XL, LSM6DSL_OUTY_H_XL),
            "z": (LSM6DSL_OUTZ_L_XL, LSM6DSL_OUTZ_H_XL),
        }
        return self.read_combined(*addr_map[axis])

    def read_gyro(self, axis):
        """
        Reads gyroscope data for a specific axis.
        :param axis: Axis identifier ('x', 'y', or 'z').
        :return: Gyroscope value for the specified axis.
        """
        addr_map = {
            "x": (LSM6DSL_OUTX_L_G, LSM6DSL_OUTX_H_G),
            "y": (LSM6DSL_OUTY_L_G, LSM6DSL_OUTY_H_G),
            "z": (LSM6DSL_OUTZ_L_G, LSM6DSL_OUTZ_H_G),
        }
        return self.read_combined(*addr_map[axis])

    def initialize_imu(self):
        """
        Configures IMU registers for operation.
        :return: True if the IMU is detected and initialized successfully, False otherwise.
        """
        try:
            if LSM6DSL_ADDRESS not in self.i2c.scan():
                self.logger.error("IMU not detected on I2C bus.")
                return False

            # Configure accelerometer
            self.write_register(LSM6DSL_CTRL1_XL, 0b10011111)  # ODR 3.33kHz, ±8g
            self.write_register(LSM6DSL_CTRL8_XL, 0b11001000)  # LPF settings

            # Configure gyroscope
            self.write_register(LSM6DSL_CTRL2_G, 0b10011100)  # ODR 3.33kHz, 2000dps

            # Common settings
            self.write_register(LSM6DSL_CTRL3_C, 0b01000100)  # Enable BDU, auto-increment

            self.logger.info("IMU initialized successfully.")
            return True
        except Exception as e:
            self.logger.exception(f"Failed to initialize IMU: {e}")
            return False