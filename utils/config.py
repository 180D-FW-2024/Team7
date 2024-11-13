# Constants for BerryIMU
RAD_TO_DEG = 57.29578  # Conversion factor
G_GAIN = 0.070         # Gyro sensitivity [deg/s/LSB]
AA = 0.40              # Complementary filter constant to balance gyro/acc influence

# Bowling Physics Constants
BALL_MASS = 6.0        # Mass of the bowling ball (kg)
PIN_MASS = 1.5         # Mass of a bowling pin (kg)
FRICTION_COEFF = 0.01  # Friction coefficient for the bowling lane

# I2C Settings
I2C_SDA_PIN = 0        # SDA pin for I2C
I2C_SCL_PIN = 1        # SCL pin for I2C
I2C_FREQ = 100000      # Frequency for I2C communication (Hz)

# LSM6DSL Configuration
LSM6DSL_ACCEL_CONFIG = {
    "odr": 0b10011111,  # Output data rate: 3.33 kHz
    "scale": 0b00000000 # +/- 2g
}

LSM6DSL_GYRO_CONFIG = {
    "odr": 0b10011100,  # Output data rate: 3.33 kHz
    "scale": 0b00000000 # +/- 245 dps
}

# Logger Settings
LOG_FILE = "server.log"
LOG_LEVEL = "INFO"

# Other Settings
SAMPLE_RATE = 0.01     # Time between IMU readings (seconds)