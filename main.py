from imu.berryimu import BerryIMU
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    imu = BerryIMU()
    if imu.initialize():
        imu.loop()

    # Uncomment for MockkIMU (Python Interpreter)
    # i2c_bus = MockI2CBus()
    # imu = BerryIMU(i2c_bus)


if __name__ == "__main__":
    main()
