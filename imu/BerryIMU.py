# Custom driver for BerryIMU

"""
BerryIMU Data Handler
- Initializes and manages data retrieval from teh BerryIMU on RPi Pico W
- Processes IMU data to stabilize angle calculations
- Logs and exports IMU data to CSV for analysis

BerryIMU Specifics:
https://ozzmaker.com/product/berryimu-accelerometer-gyroscope-magnetometer-barometricaltitude-sensor/

BerryIMU Interfacing Guide can be found here:
https://ozzmaker.com/berryimu/

GitHub Repository from Ozzmaker:
https://github.com/ozzmaker/BerryIMU

Gyros: Measure rate of rotation, which is tracked over time to calculate current angle
Accelerometer: Used to sense static and dynamic acceleration (good for quick sharp movements)

Always combine angles to overcome gryo drift and accelerometer noise
- Complementary filter: Current Angle = 98% x (current angle + gryo rotation rate) + (2% Accelerometer)

IMU and I2C:
- BerryIMUv3 uses a LSM6DSL that consists of 3-axis gyroscope and a 3-axis accelerometer
- Two signals associated with the I2C bus:
    - Serial Data Line (SDL)
    - Serial Clock Line (SLC)

LSM6DSL Addresses:
- Gyroscope: 0x6a
- Accelerometer: 0x1c

"""
import math
import utime
import logging
from imu.i2cbus import I2CBus
from LSM6DSL import *
from utils.config import RAD_TO_DEG, G_GAIN, AA


class BerryIMU:
    """
    Handles interactions with the BerryIMU sensor.
    """

    def __init__(self, i2c_bus: I2CBus):
        """
        Initializes the BerryIMU handler.
        :param i2c_bus: I2CBus instance for communication.
        """
        self.i2c = i2c_bus
        self.gyro_x_angle = 0.0
        self.gyro_y_angle = 0.0
        self.cf_angle_x = 0.0
        self.cf_angle_y = 0.0
        self.logger = logging.getLogger(self.__class__.__name__)

    def initialize(self):
        """
        Initializes the IMU via the I2C bus.
        :return: True if successful, False otherwise.
        """
        try:
            success = self.i2c.initialize_imu()
            if success:
                self.logger.info("IMU initialized successfully.")
            else:
                self.logger.error("IMU initialization failed.")
            return success
        except Exception as e:
            self.logger.exception(f"Error initializing IMU: {e}")
            return False

    def read_sensors(self):
        """
        Reads raw sensor data from the IMU.
        :return: Tuple of accelerometer and gyroscope readings.
        """
        try:
            acc_x = self.i2c.read_combined(LSM6DSL_OUTX_L_XL, LSM6DSL_OUTX_H_XL)
            acc_y = self.i2c.read_combined(LSM6DSL_OUTY_L_XL, LSM6DSL_OUTY_H_XL)
            acc_z = self.i2c.read_combined(LSM6DSL_OUTZ_L_XL, LSM6DSL_OUTZ_H_XL)
            gyr_x = self.i2c.read_combined(LSM6DSL_OUTX_L_G, LSM6DSL_OUTX_H_G)
            gyr_y = self.i2c.read_combined(LSM6DSL_OUTY_L_G, LSM6DSL_OUTY_H_G)
            gyr_z = self.i2c.read_combined(LSM6DSL_OUTZ_L_G, LSM6DSL_OUTZ_H_G)
            return acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z
        except Exception as e:
            self.logger.exception(f"Error reading sensors: {e}")
            return 0, 0, 0, 0, 0, 0

    def process_data(self, acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, loop_time):
        """
        Processes raw IMU data using a complementary filter.
        :return: Filtered angles (X, Y).
        """
        try:
            # Gyroscope rates
            rate_gyr_x = gyr_x * G_GAIN
            rate_gyr_y = gyr_y * G_GAIN

            # Update gyroscope angles
            self.gyro_x_angle += rate_gyr_x * loop_time
            self.gyro_y_angle += rate_gyr_y * loop_time

            # Accelerometer angles
            acc_x_angle = math.atan2(acc_y, acc_z) * RAD_TO_DEG
            acc_y_angle = math.atan2(acc_z, acc_x) * RAD_TO_DEG

            # Complementary filter
            self.cf_angle_x = (
                AA * (self.cf_angle_x + rate_gyr_x * loop_time) + (1 - AA) * acc_x_angle
            )
            self.cf_angle_y = (
                AA * (self.cf_angle_y + rate_gyr_y * loop_time) + (1 - AA) * acc_y_angle
            )

            return self.cf_angle_x, self.cf_angle_y
        except Exception as e:
            self.logger.exception(f"Error processing data: {e}")
            return 0.0, 0.0

    def loop(self):
        """
        Main loop for reading and processing IMU data with minimal latency.
        """
        self.logger.info("Starting IMU processing loop...")
        prev_time = utime.ticks_us()  # Initialize the previous timestamp

        while True:
            try:
                # Calculate loop time in seconds
                curr_time = utime.ticks_us()
                loop_time = (curr_time - prev_time) / 1_000_000
                prev_time = curr_time

                # Read sensor data
                acc_data = self.read_sensors()
                if acc_data is None:
                    self.logger.warning("Skipping iteration due to sensor read error.")
                    continue

                # Unpack sensor data
                acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z = acc_data

                # Process sensor data
                cf_angle_x, cf_angle_y = self.process_data(
                    acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, loop_time
                )

                # Log or print results (for debugging or monitoring)
                self.logger.info(f"CF Angles: X={cf_angle_x:.2f}, Y={cf_angle_y:.2f}")
                self.logger.debug(f"Loop Time: {loop_time:.6f} seconds")

            except KeyboardInterrupt:
                self.logger.info("Loop interrupted by user. Exiting...")
                break
            except Exception as e:
                self.logger.exception(f"Error in loop: {e}")
