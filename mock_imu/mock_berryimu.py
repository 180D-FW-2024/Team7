import math
import logging
from unittest.mock import MagicMock
from utils.config import (
    RAD_TO_DEG,
    G_GAIN,
    AA,
)  # Ensure these are available in your environment


class MockBerryIMU:
    """
    Mock class to simulate BerryIMU for testing without hardware.
    """

    def __init__(self, i2c_bus):
        self.i2c = i2c_bus
        self.gyro_x_angle = 0.0
        self.gyro_y_angle = 0.0
        self.cf_angle_x = 0.0
        self.cf_angle_y = 0.0
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Mock BerryIMU initialized.")

    def initialize(self):
        """
        Simulates initializing the BerryIMU.
        """
        return self.i2c.initialize_imu()

    def read_sensors(self):
        """
        Simulates reading raw sensor data from the IMU.
        """
        acc_x = self.i2c.read_combined(0x28, 0x29)  # Replace with real registers
        acc_y = self.i2c.read_combined(0x2A, 0x2B)
        acc_z = self.i2c.read_combined(0x2C, 0x2D)
        gyr_x = self.i2c.read_combined(0x10, 0x11)
        gyr_y = self.i2c.read_combined(0x12, 0x13)
        gyr_z = self.i2c.read_combined(0x14, 0x15)
        self.logger.debug(
            f"Mock read: ACC=({acc_x}, {acc_y}, {acc_z}), GYR=({gyr_x}, {gyr_y}, {gyr_z})"
        )
        return acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z

    def process_data(self, acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, loop_time):
        """
        Simulates processing raw IMU data using a complementary filter.
        """
        rate_gyr_x = gyr_x * G_GAIN
        rate_gyr_y = gyr_y * G_GAIN

        self.gyro_x_angle += rate_gyr_x * loop_time
        self.gyro_y_angle += rate_gyr_y * loop_time

        acc_x_angle = math.atan2(acc_y, acc_z) * RAD_TO_DEG
        acc_y_angle = math.atan2(acc_z, acc_x) * RAD_TO_DEG

        self.cf_angle_x = (
            AA * (self.cf_angle_x + rate_gyr_x * loop_time) + (1 - AA) * acc_x_angle
        )
        self.cf_angle_y = (
            AA * (self.cf_angle_y + rate_gyr_y * loop_time) + (1 - AA) * acc_y_angle
        )

        return self.cf_angle_x, self.cf_angle_y
