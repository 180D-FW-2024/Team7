"""
LSM6DSL Register Addresses and Constants
This file provides register addresses and configuration constants for the LSM6DSL IMU.
The LSM6DSL is used in the BerryIMU and allows access to accelerometer, gyroscope, 
and other motion-related data.
"""

# I2C Address
LSM6DSL_ADDRESS = 0x6A  # Default I2C address for the LSM6DSL IMU

# Identification Register
LSM6DSL_WHO_AM_I = (
    0x0F  # WHO_AM_I register to check if LSM6DSL is detected on the I2C bus
)

# Control Registers for Accelerometer and Gyroscope Configuration
LSM6DSL_CTRL1_XL = 0x10  # Control register for accelerometer settings
LSM6DSL_CTRL2_G = 0x11  # Control register for gyroscope settings
LSM6DSL_CTRL3_C = 0x12  # Control register for power and block data update settings
LSM6DSL_CTRL4_C = 0x13  # Control register for interrupt and other settings
LSM6DSL_CTRL8_XL = 0x10  # Additional control register for accelerometer filtering
LSM6DSL_CTRL10_C = 0x19  # Control register for enabling additional features

# Interrupt Configuration
LSM6DSL_INT1_CTR = 0x0D  # Control for INT1 pin configuration
LSM6DSL_MD1_CFG = 0x5E  # Mode configuration for interrupt signals on INT1
LSM6DSL_MD2_CFG = 0x5F  # Mode configuration for interrupt signals on INT2

# Wake-Up and Tap Detection
LSM6DSL_WAKE_UP_SRC = 0x1B  # Wake-up source register
LSM6DSL_WAKE_UP_THS = 0x5B  # Threshold for wake-up events
LSM6DSL_WAKE_UP_DUR = 0x5C  # Duration setting for wake-up events
LSM6DSL_TAP_CFG = 0x58  # Configuration register for tap detection
LSM6DSL_TAP_CFG1 = 0x58  # Configuration register for 6D orientation and tap detection
LSM6DSL_TAP_THS_6D = 0x59  # Threshold for 6D orientation detection
LSM6DSL_INT_DUR2 = 0x5A  # Duration setting for double-tap detection
LSM6DSL_FREE_FALL = 0x5D  # Configuration for free-fall detection

# Step Counter
LSM6DSL_STEP_COUNTER_L = 0x4B  # Low byte of step counter
LSM6DSL_STEP_COUNTER_H = 0x4C  # High byte of step counter

# Temperature Data Output Registers
LSM6DSL_OUT_L_TEMP = 0x20  # Low byte of temperature data
LSM6DSL_OUT_H_TEMP = 0x21  # High byte of temperature data

# Accelerometer Data Output Registers
LSM6DSL_OUTX_L_XL = 0x28  # Low byte of accelerometer X-axis data
LSM6DSL_OUTX_H_XL = 0x29  # High byte of accelerometer X-axis data
LSM6DSL_OUTY_L_XL = 0x2A  # Low byte of accelerometer Y-axis data
LSM6DSL_OUTY_H_XL = 0x2B  # High byte of accelerometer Y-axis data
LSM6DSL_OUTZ_L_XL = 0x2C  # Low byte of accelerometer Z-axis data
LSM6DSL_OUTZ_H_XL = 0x2D  # High byte of accelerometer Z-axis data

# Gyroscope Data Output Registers
LSM6DSL_OUTX_L_G = 0x22  # Low byte of gyroscope X-axis data
LSM6DSL_OUTX_H_G = 0x23  # High byte of gyroscope X-axis data
LSM6DSL_OUTY_L_G = 0x24  # Low byte of gyroscope Y-axis data
LSM6DSL_OUTY_H_G = 0x25  # High byte of gyroscope Y-axis data
LSM6DSL_OUTZ_L_G = 0x26  # Low byte of gyroscope Z-axis data
LSM6DSL_OUTZ_H_G = 0x27  # High byte of gyroscope Z-axis data

# Additional Functional Source Register
LSM6DSL_FUNC_SRC1 = 0x53  # Source register for additional functions
