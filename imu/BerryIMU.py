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
Accelerometer: Used to sense static and dynamic accelaration (good for quick sharp movements)

Always combine angles to overcome gryo drift and accelerometer noise
- Complementary filter: Current Angle = 98% x (current angle + gryo rotation rate) + (2% Accelerometer)

IMU and I2C:
- BerryIMUv3 uses a LSM6DSL that cosnists of 3-axis gryoscope and a 3-axis accelerometer
- Two signlas associated with the I2C bus:
    - Serial Data Line (SDL)
    - Serial Clock Line (SLC)

LSM6DSL Adresses:
- Gyroscope: 0x6a
- Accelerometer: 0x1c

"""

import utime
import csv
import math

import IMU_I2C as IMU
import motion_calulations as motion
from physics.bowling_physics import BowlingPhysics

# from utils.constants import RAD_TO_DEG, G_GAIN, AA, BALL_MASS, FRICTION, PIN_MASS
from utils.logger import get_logger


logger = get_logger(__name__)  # Set up logging to tack data processing/issues

# physics = BowlingPhysics()

# Angle variables to store angles
import utime
import math
from LSM6DSL import *
import machine

# Comment out one of the below lines
# import IMU_SPI as IMU
import IMU_I2C as IMU

RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070  # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA = 0.40  # Complementary filter constant

gyroXangle = 0.0
gyroYangle = 0.0
gyroZangle = 0.0
CFangleX = 0.0
CFangleY = 0.0


IMU.initIMU()  # Initialise the accelerometer, gyroscope and compass


a = utime.ticks_us()

while True:

    # Read the accelerometer,gyroscope and magnetometer values
    ACCx = IMU.readACCx()
    ACCy = IMU.readACCy()
    ACCz = IMU.readACCz()
    GYRx = IMU.readGYRx()
    GYRy = IMU.readGYRy()
    GYRz = IMU.readGYRz()

    b = utime.ticks_us() - a
    a = utime.ticks_us()
    LP = b / (1000000 * 1.0)
    outputString = "Loop Time %5.3f " % (LP)

    # Convert Gyro raw to degrees per second
    rate_gyr_x = GYRx * G_GAIN
    rate_gyr_y = GYRy * G_GAIN
    rate_gyr_z = GYRz * G_GAIN

    # Calculate the angles from the gyro.
    gyroXangle += rate_gyr_x * LP
    gyroYangle += rate_gyr_y * LP
    gyroZangle += rate_gyr_z * LP

    # Convert Accelerometer values to degrees
    AccXangle = math.atan2(ACCy, ACCz) * RAD_TO_DEG
    AccYangle = (math.atan2(ACCz, ACCx) + M_PI) * RAD_TO_DEG

    # convert the values to -180 and +180
    if AccYangle > 90:
        AccYangle -= 270.0
    else:
        AccYangle += 90.0

    # Complementary filter used to combine the accelerometer and gyro values.
    CFangleX = AA * (CFangleX + rate_gyr_x * LP) + (1 - AA) * AccXangle
    CFangleY = AA * (CFangleY + rate_gyr_y * LP) + (1 - AA) * AccYangle

    if 0:  # Change to '0' to stop showing the angles from the accelerometer
        outputString += "#  ACCX Angle %5.2f ACCY Angle %5.2f  #  " % (
            AccXangle,
            AccYangle,
        )

    if 0:  # Change to '0' to stop  showing the angles from the gyro
        outputString += (
            "\t# GRYX Angle %5.2f  GYRY Angle %5.2f  GYRZ Angle %5.2f # "
            % (gyroXangle, gyroYangle, gyroZangle)
        )

    if 1:  # Change to '0' to stop  showing the angles from the complementary filter
        outputString += "\t#  CFangleX Angle %5.2f   CFangleY Angle %5.2f  #" % (
            CFangleX,
            CFangleY,
        )

    print(outputString)
