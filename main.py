from imu.berryimu import BerryIMU
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    imu = BerryIMU()
    if imu.initialize():
        imu.loop()


if __name__ == "__main__":
    main()
