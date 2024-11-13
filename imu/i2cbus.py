import machine
import logging
from imu.LSM6DSL import *

FREQ = 100000
SDA_PIN = 0
SCL_PIN = 1


class I2CBus:
    """
    Handles I2C communication with the BerryIMU.
    """

    def __init__(self, sda_pin=SDA_PIN, scl_pin=SCL_PIN, freq=FREQ):
        """
        Initializes the I2C bus with specified pins and frequency.
        :param sda_pin: GPIO pin for SDA.
        :param scl_pin: GPIO pin for SCL.
        :param freq: I2C bus frequency in Hz.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        try:
            self.i2c = machine.I2C(
                0, sda=machine.Pin(sda_pin), scl=machine.Pin(scl_pin), freq=freq
            )
            self.logger.info("I2C bus initialized successfully.")
        except Exception as e:
            self.logger.exception(f"Failed to initialize I2C: {e}")
            raise RuntimeError("Failed to initialize I2C") from e

    def write_register(self, register, data):
        """
        Writes a byte to a specified register.
        :param register: Register address.
        :param data: Data to write (1 byte).
        """
        try:
            self.i2c.writeto_mem(LSM6DSL_ADDRESS, register, bytes([data]))
            self.logger.debug(
                f"Write: Address={LSM6DSL_ADDRESS}, Register={register}, Data={data}"
            )
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
            self.logger.debug(
                f"Read: Address={LSM6DSL_ADDRESS}, Register={register}, Data={data}"
            )
            return data
        except Exception as e:
            self.logger.exception(f"Failed to read from register {register}: {e}")
            return b"\x00" * length  # Default to zeros on error

    def read_combined(self, low_addr, high_addr):
        """
        Reads and combines low and high byte registers into a 16-bit signed value.
        :param low_addr: Address of the low byte register.
        :param high_addr: Address of the high byte register.
        :return: Signed 16-bit value.
        """
        try:
            low = self.read_register(low_addr)[0]
            high = self.read_register(high_addr)[0] << 8
            value = low | high
            return value if value < 32768 else value - 65536
        except Exception as e:
            self.logger.exception(
                f"Failed to read combined value from {low_addr} and {high_addr}: {e}"
            )
            return 0  # Default to zero on error

    def initialize_imu(self):
        """
        Configures IMU registers for operation.
        :return: True if the IMU is detected and initialized successfully, False otherwise.
        """
        try:
            if LSM6DSL_ADDRESS not in self.i2c.scan():
                self.logger.error("IMU not detected on I2C bus.")
                return False

            # Initialize accelerometer
            self.write_register(LSM6DSL_CTRL1_XL, 0b10011111)  # ODR 3.33kHz, ±8g
            self.write_register(LSM6DSL_CTRL8_XL, 0b11001000)  # LPF settings

            # Initialize gyroscope
            self.write_register(LSM6DSL_CTRL2_G, 0b10011100)  # ODR 3.33kHz, 2000dps

            # Common settings
            self.write_register(
                LSM6DSL_CTRL3_C, 0b01000100
            )  # Enable BDU, auto-increment

            self.logger.info("IMU initialized successfully.")
            return True
        except Exception as e:
            self.logger.exception(f"Failed to initialize IMU: {e}")
            return False
