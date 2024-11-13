import logging
import random


class MockI2CBus:
    """
    Mock class to simulate I2C communication for testing without hardware.
    """

    def __init__(self, sda_pin=0, scl_pin=1, freq=100000):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Mock I2C bus initialized.")
        self.mock_data = {
            "gyro": [0, 0, 0],  # Mock gyroscope readings
            "acc": [0, 0, 9.8],  # Mock accelerometer readings
        }

    def write_register(self, register, data):
        """
        Simulates writing a byte to a register.
        """
        self.logger.debug(f"Mock write: Register={register}, Data={data}")

    def read_register(self, register, length=1):
        """
        Simulates reading from a register.
        """
        self.logger.debug(f"Mock read: Register={register}, Length={length}")
        return bytes([random.randint(0, 255) for _ in range(length)])

    def read_combined(self, low_addr, high_addr):
        """
        Simulates reading and combining low and high byte registers.
        """
        low = random.randint(0, 255)
        high = random.randint(0, 255)
        value = low | (high << 8)
        self.logger.debug(f"Mock combined read: Low={low}, High={high}, Value={value}")
        return value if value < 32768 else value - 65536

    def initialize_imu(self):
        """
        Simulates IMU initialization.
        """
        self.logger.info("Mock IMU initialized successfully.")
        return True
