# Custom driver for BerryIMU

"""
BerryIMU Data Handler
- Intiliazes and manages data retrieval from teh BerryIMU on RPi Pico W
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
from imu.i2cbus import I2CBus
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

    def initialize(self):
        """
        Initializes the IMU via the I2C bus.
        :return: True if successful, False otherwise.
        """
        return self.i2c.initialize_imu()

    def read_sensors(self):
        """
        Reads raw sensor data from the IMU.
        :return: Tuple of accelerometer and gyroscope readings.
        """
        acc_x = self.i2c.read_acc_x()
        acc_y = self.i2c.read_acc_y()
        acc_z = self.i2c.read_acc_z()
        gyr_x = self.i2c.read_gyro_x()
        gyr_y = self.i2c.read_gyro_y()
        gyr_z = self.i2c.read_gyro_z()
        return acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z

    def process_data(self, acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, loop_time):
        """
        Processes raw IMU data using a complementary filter.
        :return: Filtered angles (X, Y).
        """
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
        self.cf_angle_x = AA * (self.cf_angle_x + rate_gyr_x * loop_time) + (1 - AA) * acc_x_angle
        self.cf_angle_y = AA * (self.cf_angle_y + rate_gyr_y * loop_time) + (1 - AA) * acc_y_angle

        return self.cf_angle_x, self.cf_angle_y

    def loop(self):
        """
        Main loop for reading and processing IMU data.
        """
        import time
        prev_time = time.ticks_us()

        while True:
            curr_time = time.ticks_us()
            loop_time = (curr_time - prev_time) / 1_000_000  # Convert to seconds
            prev_time = curr_time

            acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z = self.read_sensors()
            cf_angle_x, cf_angle_y = self.process_data(acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, loop_time)

            print(f"CF Angles: X={cf_angle_x:.2f}, Y={cf_angle_y:.2f}")