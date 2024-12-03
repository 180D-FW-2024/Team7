import sys
import signal
import time
import logging
from dataclasses import dataclass, asdict
import json
import os

import IMU


@dataclass
class MagnetometerCalibration:
    """
    Dataclass to store magnetometer calibration values
    """
    magXmin: int = 32767
    magYmin: int = 32767
    magZmin: int = 32767
    magXmax: int = -32767
    magYmax: int = -32767
    magZmax: int = -32767


class IMUCalibrator:
    """
    Comprehensive IMU Calibration Tool
    """

    def __init__(self, calibration_file='imu_calibration.json'):
        """
        Initialize calibration process

        :param calibration_file: File to save/load calibration data
        """
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        self.calibration = MagnetometerCalibration()
        self.calibration_file = calibration_file

    def start_calibration(self, duration=30):
        """
        Start magnetometer calibration

        :param duration: Duration of calibration in seconds
        :return: Calibration results
        """
        self.logger.info("Starting IMU Magnetometer Calibration")
        self.logger.info("Rotate your IMU in all directions for best results")

        # Detect and initialize IMU
        IMU.detectIMU()
        if IMU.BerryIMUversion == 99:
            self.logger.error("No BerryIMU found")
            return None

        IMU.initIMU()

        start_time = time.time()

        try:
            while time.time() - start_time < duration:
                # Read magnetometer values
                MAGx = IMU.readMAGx()
                MAGy = IMU.readMAGy()
                MAGz = IMU.readMAGz()

                # Update min/max values
                self.calibration.magXmin = min(self.calibration.magXmin, MAGx)
                self.calibration.magYmin = min(self.calibration.magYmin, MAGy)
                self.calibration.magZmin = min(self.calibration.magZmin, MAGz)

                self.calibration.magXmax = max(self.calibration.magXmax, MAGx)
                self.calibration.magYmax = max(self.calibration.magYmax, MAGy)
                self.calibration.magZmax = max(self.calibration.magZmax, MAGz)

                # Print current calibration values
                print(f"magXmin: {self.calibration.magXmin}, magXmax: {self.calibration.magXmax}")
                print(f"magYmin: {self.calibration.magYmin}, magYmax: {self.calibration.magYmax}")
                print(f"magZmin: {self.calibration.magZmin}, magZmax: {self.calibration.magZmax}")

                time.sleep(0.1)  # Small delay to reduce CPU usage

            return self.get_calibration()

        except KeyboardInterrupt:
            self.logger.info("Calibration interrupted by user")
            return self.get_calibration()

    def get_calibration(self):
        """
        Get current calibration values

        :return: Dict of calibration values
        """
        return asdict(self.calibration)

    def save_calibration(self):
        """
        Save calibration to JSON file
        """
        try:
            with open(self.calibration_file, 'w') as f:
                json.dump(self.get_calibration(), f)
            self.logger.info(f"Calibration saved to {self.calibration_file}")
        except Exception as e:
            self.logger.error(f"Error saving calibration: {e}")

    def load_calibration(self):
        """
        Load calibration from JSON file

        :return: Loaded calibration or None
        """
        try:
            if os.path.exists(self.calibration_file):
                with open(self.calibration_file, 'r') as f:
                    loaded_cal = json.load(f)
                self.calibration = MagnetometerCalibration(**loaded_cal)
                self.logger.info("Calibration loaded successfully")
                return loaded_cal
            else:
                self.logger.warning("No calibration file found")
                return None
        except Exception as e:
            self.logger.error(f"Error loading calibration: {e}")
            return None


def main():
    """
    Main function to run calibration
    """
    calibrator = IMUCalibrator()

    # Optional: Load existing calibration
    existing_cal = calibrator.load_calibration()

    # Start calibration
    calibration = calibrator.start_calibration()

    if calibration:
        # Print calibration values
        print("\nCalibration Values:")
        for key, value in calibration.items():
            print(f"{key}: {value}")

        # Save calibration
        calibrator.save_calibration()


if __name__ == "__main__":
    main()