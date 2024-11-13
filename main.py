# from imu.berryimu import BerryIMU
from utils.logger import get_logger

from mock_imu.mock_i2c import MockI2CBus
from mock_imu.mock_berryimu import MockBerryIMU
from mock_imu.mock_i2c import MockI2CBus

logger = get_logger(__name__)


def main():
    # imu = BerryIMU()
    # if imu.initialize():
    # imu.loop()

    # Uncomment for MockkIMU (Python Interpreter)

    # Initialize mock objects
    i2c_bus = MockI2CBus()
    imu = MockBerryIMU(i2c_bus)


if __name__ == "__main__":
    main()
