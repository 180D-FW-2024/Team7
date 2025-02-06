import logging
from time import sleep
from bluezero import adapter, device, GATT, tools

# UUIDs from your peripheral script
IMU_SERVICE_UUID = '1b9998a2-1234-5678-1234-56789abcdef0'
ACCEL_CHAR_UUID = '2713d05a-1234-5678-1234-56789abcdef1'
GYRO_CHAR_UUID = '2713d05b-1234-5678-1234-56789abcdef2'
MAG_CHAR_UUID = '2713d05c-1234-5678-1234-56789abcdef3'

# Set up logging
logger = tools.create_module_logger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Central:
    """Create a BLE instance taking the Central role."""

    def __init__(self, device_addr, adapter_addr=None):
        # Initialize adapter
        if adapter_addr is None:
            self.dongle = adapter.Adapter()
            logger.debug("Adapter is: %s", self.dongle.address)
        else:
            self.dongle = adapter.Adapter(adapter_addr)

        # Ensure the adapter is powered
        if not self.dongle.powered:
            self.dongle.powered = True
            logger.info("Adapter was off, now powered on")

        # Connect to the remote device
        self.rmt_device = device.Device(self.dongle.address, device_addr)
        self._characteristics = []

    def add_characteristic(self, srv_uuid, chrc_uuid):
        """
        Specify a characteristic of interest on the remote device.

        :param srv_uuid: 128-bit UUID
        :param chrc_uuid: 128-bit UUID
        """
        chrc_hndl = GATT.Characteristic(self.dongle.address,
                                        self.rmt_device.address,
                                        srv_uuid,
                                        chrc_uuid)
        self._characteristics.append(chrc_hndl)
        return chrc_hndl

    def load_gatt(self):
        """
        Once connected to the remote device, load the GATT database.
        """
        for chrc in self._characteristics:
            available = chrc.resolve_gatt()
            if available:
                logger.info("Service: %s, Characteristic: %s added",
                            chrc.srv_uuid, chrc.chrc_uuid)
            else:
                logger.warning("Service: %s, Characteristic: %s not available on device: %s",
                               chrc.srv_uuid, chrc.chrc_uuid, chrc.device_addr)

    def connect(self, timeout=35):
        """
        Initiate connection to the remote device.

        :param timeout: (optional) seconds to wait for connection.
        """
        logger.info("Connecting to device...")
        self.rmt_device.connect(timeout=timeout)

        while not self.rmt_device.services_resolved:
            logger.info("Waiting for services to resolve...")
            sleep(1)

        logger.info("Device connected. Services resolved.")
        self.load_gatt()

    def read_characteristics(self):
        """
        Read values from characteristics (e.g., accelerometer, gyroscope, magnetometer).
        """
        for chrc in self._characteristics:
            value = chrc.read_value()
            logger.info("Characteristic %s value: %s", chrc.chrc_uuid, value)

    def disconnect(self):
        """Disconnect from the remote device."""
        logger.info("Disconnecting from device...")
        self.rmt_device.disconnect()
        logger.info("Device disconnected.")


if __name__ == '__main__':
    # Replace this with the Bluetooth address of your peripheral
    DEVICE_ADDRESS = "D8:3A:DD:EB:EE:63"  # Example address

    try:
        # Initialize central device
        central = Central(DEVICE_ADDRESS)

        # Add IMU characteristics
        central.add_characteristic(IMU_SERVICE_UUID, ACCEL_CHAR_UUID)
        central.add_characteristic(IMU_SERVICE_UUID, GYRO_CHAR_UUID)
        central.add_characteristic(IMU_SERVICE_UUID, MAG_CHAR_UUID)

        # Connect and read values
        central.connect()
        central.read_characteristics()

    except KeyboardInterrupt:
        logger.info("Terminating connection...")
        if 'central' in locals():
            central.disconnect()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
