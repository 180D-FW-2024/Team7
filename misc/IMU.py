import smbus2
import time
import logging


class IMUSensor:
    """
    A comprehensive class for handling IMU sensor interactions
    Supports BerryIMUv1, BerryIMUv2, and BerryIMUv3
    """

    # Sensor address constants
    LSM9DS0_MAG_ADDRESS = 0x1E
    LSM9DS0_ACC_ADDRESS = 0x1E
    LSM9DS0_GYR_ADDRESS = 0x6A

    LSM9DS1_MAG_ADDRESS = 0x1C
    LSM9DS1_ACC_ADDRESS = 0x6A
    LSM9DS1_GYR_ADDRESS = 0x6A

    LSM6DSL_ADDRESS = 0x6A
    LIS2MDL_ADDRESS = 0x1E

    def __init__(self, bus_number=1):
        """
        Initialize IMU sensor communication

        :param bus_number: I2C bus number (default 1 for Raspberry Pi)
        """
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        try:
            self.bus = smbus2.SMBus(bus_number)
        except Exception as e:
            self.logger.error(f"Failed to initialize I2C bus: {e}")
            raise

        self.BerryIMUversion = None
        self.detected_sensors = {}

    def detectIMU(self):
        """
        Detect the version of BerryIMU connected

        :return: IMU version number or 99 if no IMU detected
        """
        try:
            # Attempt to detect IMU version
            # This is a placeholder - you'll need to implement actual detection logic
            # based on your specific sensor chipsets

            # Example detection logic (customize based on your specific sensors)
            try:
                # Try LSM9DS0
                self.bus.read_byte_data(self.LSM9DS0_MAG_ADDRESS, 0x0F)
                self.BerryIMUversion = 1
                self.detected_sensors['mag'] = 'LSM9DS0'
                self.detected_sensors['acc'] = 'LSM9DS0'
                self.detected_sensors['gyr'] = 'LSM9DS0'
            except:
                try:
                    # Try LSM6DSL & LIS2MDL
                    self.bus.read_byte_data(self.LSM6DSL_ADDRESS, 0x0F)
                    self.BerryIMUversion = 3
                    self.detected_sensors['mag'] = 'LIS2MDL'
                    self.detected_sensors['acc'] = 'LSM6DSL'
                    self.detected_sensors['gyr'] = 'LSM6DSL'
                except:
                    self.BerryIMUversion = 99
                    self.logger.error("No compatible IMU detected")

            return self.BerryIMUversion

        except Exception as e:
            self.logger.error(f"Error detecting IMU: {e}")
            self.BerryIMUversion = 99
            return self.BerryIMUversion

    def initIMU(self):
        """
        Initialize the IMU sensors based on detected version
        """
        if self.BerryIMUversion == 99:
            self.logger.error("Cannot initialize - no IMU detected")
            return False

        try:
            # Implement sensor-specific initialization
            # This is a placeholder - you'll need to add specific initialization
            # for each sensor type (LSM9DS0, LSM9DS1, LSM6DSL)
            if self.BerryIMUversion == 1:  # LSM9DS0
                # Add LSM9DS0 specific initialization
                pass
            elif self.BerryIMUversion == 3:  # LSM6DSL & LIS2MDL
                # Add LSM6DSL and LIS2MDL specific initialization
                pass

            return True
        except Exception as e:
            self.logger.error(f"Error initializing IMU: {e}")
            return False

    def _read_sensor_data(self, address, register, num_bytes=2):
        """
        Generic method to read sensor data

        :param address: I2C device address
        :param register: Register to read from
        :param num_bytes: Number of bytes to read
        :return: Raw sensor value
        """
        try:
            if num_bytes == 2:
                # Read 16-bit value (little-endian)
                low = self.bus.read_byte_data(address, register)
                high = self.bus.read_byte_data(address, register + 1)
                return self._combine_bytes(low, high)
            else:
                # For 8-bit or other byte counts
                return self.bus.read_byte_data(address, register)
        except Exception as e:
            self.logger.error(f"Error reading sensor data from {hex(address)}: {e}")
            return 0

    def _combine_bytes(self, low, high):
        """
        Combine two bytes into a signed 16-bit integer

        :param low: Low byte
        :param high: High byte
        :return: Signed 16-bit value
        """
        value = (high << 8) | low
        # Convert to signed 16-bit value
        return value if value < 32768 else value - 65536

    def readACCx(self):
        """Read X-axis Accelerometer value"""
        if self.BerryIMUversion == 1:
            return self._read_sensor_data(self.LSM9DS0_ACC_ADDRESS, 0x28)
        elif self.BerryIMUversion == 3:
            return self._read_sensor_data(self.LSM6DSL_ADDRESS, 0x28)
        return 0

    def readACCy(self):
        """Read Y-axis Accelerometer value"""
        if self.BerryIMUversion == 1:
            return self._read_sensor_data(self.LSM9DS0_ACC_ADDRESS, 0x2A)
        elif self.BerryIMUversion == 3:
            return self._read_sensor_data(self.LSM6DSL_ADDRESS, 0x2A)
        return 0

    def readACCz(self):
        """Read Z-axis Accelerometer value"""
        if self.BerryIMUversion == 1:
            return self._read_sensor_data(self.LSM9DS0_ACC_ADDRESS, 0x2C)
        elif self.BerryIMUversion == 3:
            return self._read_sensor_data(self.LSM6DSL_ADDRESS, 0x2C)
        return 0

    def readGYRx(self):
        """Read X-axis Gyroscope value"""
        if self.BerryIMUversion == 1:
            return self._read_sensor_data(self.LSM9DS0_GYR_ADDRESS, 0x28)
        elif self.BerryIMUversion == 3:
            return self._read_sensor_data(self.LSM6DSL_ADDRESS, 0x22)
        return 0

    def readGYRy(self):
        """Read Y-axis Gyroscope value"""
        if self.BerryIMUversion == 1:
            return self._read_sensor_data(self.LSM9DS0_GYR_ADDRESS, 0x2A)
        elif self.BerryIMUversion == 3:
            return self._read_sensor_data(self.LSM6DSL_ADDRESS, 0x24)
        return 0

    def readGYRz(self):
        """Read Z-axis Gyroscope value"""
        if self.BerryIMUversion == 1:
            return self._read_sensor_data(self.LSM9DS0_GYR_ADDRESS, 0x2C)
        elif self.BerryIMUversion == 3:
            return self._read_sensor_data(self.LSM6DSL_ADDRESS, 0x26)
        return 0

    def readMAGx(self):
        """Read X-axis Magnetometer value"""
        if self.BerryIMUversion == 1:
            return self._read_sensor_data(self.LSM9DS0_MAG_ADDRESS, 0x08)
        elif self.BerryIMUversion == 3:
            return self._read_sensor_data(self.LIS2MDL_ADDRESS, 0x28)
        return 0

    def readMAGy(self):
        """Read Y-axis Magnetometer value"""
        if self.BerryIMUversion == 1:
            return self._read_sensor_data(self.LSM9DS0_MAG_ADDRESS, 0x0A)
        elif self.BerryIMUversion == 3:
            return self._read_sensor_data(self.LIS2MDL_ADDRESS, 0x2A)
        return 0

    def readMAGz(self):
        """Read Z-axis Magnetometer value"""
        if self.BerryIMUversion == 1:
            return self._read_sensor_data(self.LSM9DS0_MAG_ADDRESS, 0x0C)
        elif self.BerryIMUversion == 3:
            return self._read_sensor_data(self.LIS2MDL_ADDRESS, 0x2C)
        return 0


# Global instance for backwards compatibility
imu_sensor = IMUSensor()
detectIMU = imu_sensor.detectIMU
initIMU = imu_sensor.initIMU
readACCx = imu_sensor.readACCx
readACCy = imu_sensor.readACCy
readACCz = imu_sensor.readACCz
readGYRx = imu_sensor.readGYRx
readGYRy = imu_sensor.readGYRy
readGYRz = imu_sensor.readGYRz
readMAGx = imu_sensor.readMAGx
readMAGy = imu_sensor.readMAGy
readMAGz = imu_sensor.readMAGz