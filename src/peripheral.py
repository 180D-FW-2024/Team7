from bluezero import adapter
from bluezero import advertisement
from bluezero import tools
from bluezero import async_tools
import struct
import time
import logging
from IMU import IMUSensor  # Ensure this is the correct path to your IMU library

# Peripheral class from documentation
from peripheral_class import Peripheral  # Import your Peripheral class correctly

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IMUAdvertisement(advertisement.Advertisement):
    """Custom BLE advertisement for the IMU Peripheral"""
    def __init__(self, device_name):
        super().__init__(0, 'peripheral')  # Instance 0
        self.local_name = device_name
        self.include_tx_power = True
        self.service_UUIDs = ['1b9998a2-1234-5678-1234-56789abcdef0']  # IMU Service UUID


class IMUPeripheral:
    """Peripheral for broadcasting IMU sensor data via BLE"""
    IMU_SERVICE_UUID = '1b9998a2-1234-5678-1234-56789abcdef0'
    ACCEL_CHAR_UUID = '2713d05a-1234-5678-1234-56789abcdef1'
    GYRO_CHAR_UUID = '2713d05b-1234-5678-1234-56789abcdef2'
    MAG_CHAR_UUID = '2713d05c-1234-5678-1234-56789abcdef3'

    def __init__(self, adapter_address=None):
        logger.info("Initializing IMU Peripheral...")

        # Get the Bluetooth adapter
        self.adapter = adapter.Adapter(adapter_address or list(adapter.Adapter.available())[0].address)
        self.adapter.powered = True
        self.adapter.discoverable = True
        self.adapter.pairable = True

        # Initialize the IMU sensor
        self.imu = IMUSensor()
        if self.imu.detectIMU() == 99:
            raise RuntimeError("No IMU detected")
        self.imu.initIMU()
        logger.info("IMU Initialized")

        # Set up advertisement
        self.advertisement = IMUAdvertisement('IMU_Sensor')
        self.ad_manager = advertisement.AdvertisingManager(self.adapter.address)

        # Add GATT characteristics
        self._setup_gatt()

    def _setup_gatt(self):
        """Configure GATT services and characteristics for BLE"""
        logger.info("Setting up GATT server...")
        self.peripheral = Peripheral(self.adapter.address, local_name="IMU_Sensor")

        # Add IMU Service
        self.peripheral.add_service(1, self.IMU_SERVICE_UUID, True)
        logger.info(f"Added service with UUID: {self.IMU_SERVICE_UUID}")

        # Add Accelerometer Characteristic
        self.peripheral.add_characteristic(
            1, 1, self.ACCEL_CHAR_UUID, [0] * 6, notifying=True, flags=['read', 'notify'],
            read_callback=self._read_accelerometer
        )
        logger.info(f"Added characteristic for Accelerometer with UUID: {self.ACCEL_CHAR_UUID}")

        # Add Gyroscope Characteristic
        self.peripheral.add_characteristic(
            1, 2, self.GYRO_CHAR_UUID, [0] * 6, notifying=True, flags=['read', 'notify'],
            read_callback=self._read_gyroscope
        )
        logger.info(f"Added characteristic for Gyroscope with UUID: {self.GYRO_CHAR_UUID}")

        # Add Magnetometer Characteristic
        self.peripheral.add_characteristic(
            1, 3, self.MAG_CHAR_UUID, [0] * 6, notifying=True, flags=['read', 'notify'],
            read_callback=self._read_magnetometer
        )
        logger.info(f"Added characteristic for Magnetometer with UUID: {self.MAG_CHAR_UUID}")

    def _read_accelerometer(self):
        """Callback to read accelerometer values"""
        x, y, z = self.imu.readACCx(), self.imu.readACCy(), self.imu.readACCz()
        logger.info(f"Accelerometer Read: X={x}, Y={y}, Z={z}")
        return list(struct.pack('<hhh', int(x), int(y), int(z)))

    def _read_gyroscope(self):
        """Callback to read gyroscope values"""
        x, y, z = self.imu.readGYRx(), self.imu.readGYRy(), self.imu.readGYRz()
        logger.info(f"Gyroscope Read: X={x}, Y={y}, Z={z}")
        return list(struct.pack('<hhh', int(x), int(y), int(z)))

    def _read_magnetometer(self):
        """Callback to read magnetometer values"""
        x, y, z = self.imu.readMAGx(), self.imu.readMAGy(), self.imu.readMAGz()
        logger.info(f"Magnetometer Read: X={x}, Y={y}, Z={z}")
        return list(struct.pack('<hhh', int(x), int(y), int(z)))

    def start(self):
        """Start advertising and serving the GATT server"""
        logger.info("Starting IMU Peripheral...")
        try:
            self.ad_manager.register_advertisement(self.advertisement, {})
            logger.info("Advertisement registered successfully")
            self.peripheral.publish()
            time.sleep(10)
            logger.info("Peripheral published and running")
        except Exception as e:
            logger.error(f"Failed to start IMU Peripheral: {e}")

    def stop(self):
        """Stop advertising and GATT server"""
        logger.info("Stopping IMU Peripheral...")
        try:
            self.peripheral.quit()
            self.ad_manager.unregister_advertisement(self.advertisement)
            logger.info("IMU Peripheral stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping IMU Peripheral: {e}")


if __name__ == '__main__':
    try:
        imu_peripheral = IMUPeripheral()
        imu_peripheral.start()
    except KeyboardInterrupt:
        logger.info("Shutting down due to KeyboardInterrupt...")
        imu_peripheral.stop()
    except Exception as e:
        logger.error(f"Fatal error occurred: {e}")
