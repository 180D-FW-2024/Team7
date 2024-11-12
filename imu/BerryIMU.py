# Custom driver for BerryIMU

"""
BerryIMU Data Handler
- Intiliazes and manages data retrieval from teh BerryIMU on RPi Pico W
- Processes IMU data to stabilize angle calculations
- Logs and exports IMU data to CSV for analysis
"""

import time
import csv
import math

from IMU_I2C import initialize_imu, read_accel_data, read_gyro_data
from motion_calculations import (
    calculate_speed,
    calculate_spin,
    calculate_momentum,
    calculate_angular_momentum,
    apply_friction,
)
from physics.bowling_physics import BowlingPhysics

from utils.constants import RAD_TO_DEG, G_GAIN, AA, BALL_MASS, FRICTION, PIN_MASS
from utils.logger import get_logger


logger = get_logger(__name__)  # Set up logging to tack data processing/issues

# physics = BowlingPhysics()

# Angle variables to store angles
gyro_angles = {"x": 0.0, "y": 0.0, "z": 0.0}
cf_angles = {"x": 0.0, "y": 0.0}  # Optional filtered angles


def complementary_filter(accel_angle, gyro_rate, delta_time, previous_angle):
    """_summary_

    Args:
        accel_angle : Angle derived from acc. data
        gyro_rate : Rate of change of the angle from gyro
        delta_time : Time inetrval for each loop
        previous_angle : Previosuly calculated angle from filter

    Returns:
        New angle that combines acc. and gyro data
    """
    return AA * (previous_angle + gyro_rate * delta_time) + (1 - AA) * accel_angle


def process_imu_data():
    """
    Main loop to read IMU data, process it using complementary filter, log to CSV.
    Reads acc and gyro values, applies sesnor fusion , and logs
    """
    last_time = time.time()  # Start time to calculate loop duraction

    # Open CSV file for writing
    with open("imu_data.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Time",
                "Accel_X",
                "Accel_Y",
                "Accel_Z",
                "Gyro_X",
                "Gyro_Y",
                "Gyro_Z",
                "CF_X",
                "CF_Y",
            ]
        )
        # Header row

        while True:
            # Read accelerometer and gyroscope data
            accel = read_accel_data()
            gyro = read_gyro_data()

            # Calculate loop time
            current_time = time.time()
            loop_time = current_time - last_time  # Duration of one loop cycle
            last_time = current_time

            # Convert gyro readings to degrees per second
            gyro_rates = {axis: gyro[axis] * G_GAIN for axis in gyro}

            # Update gyro-based angles
            for axis in gyro_angles:
                gyro_angles[axis] += gyro_rates[axis] * loop_time

            # Calculate angles from accelerometer data
            accel_angles = {
                "x": math.atan2(accel["y"], accel["z"]) * RAD_TO_DEG,
                "y": (math.atan2(accel["z"], accel["x"]) + math.pi) * RAD_TO_DEG - 180,
            }

            # Apply complementary filter
            cf_angles["x"] = complementary_filter(
                accel_angles["x"], gyro_rates["x"], loop_time, cf_angles["x"]
            )
            cf_angles["y"] = complementary_filter(
                accel_angles["y"], gyro_rates["y"], loop_time, cf_angles["y"]
            )
            writer.writerow(
                [
                    time.time(),
                    accel["x"],
                    accel["y"],
                    accel["z"],
                    gyro["x"],
                    gyro["y"],
                    gyro["z"],
                    cf_angles["x"],
                    cf_angles["y"],  # Filtered angles
                ]
            )

            # Log filtered angles
            logger.info(f"CF Angles - X: {cf_angles['x']:.2f}, Y: {cf_angles['y']:.2f}")

            time.sleep(1)  # Delay for readability
