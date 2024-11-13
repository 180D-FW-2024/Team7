from imu.i2cbus import initialize_imu, read_accel_data, read_gyro_data
from imu.berryimu import process_imu_data
from physics.bowling_physics import BowlingPhysics
from utils.logger import get_logger

logger = get_logger(__name__)

def main():
    logger.info("Starting Bowling Simulation...")

    # Initialize IMU
    if initialize_imu():
        logger.info("IMU successfully initialized.")
    else:
        logger.error("IMU initialization failed.")
        return

    physics = BowlingPhysics()

    process_imu_data()

if __name__ == "__main__":
    main()