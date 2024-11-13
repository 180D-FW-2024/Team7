from unittest.mock import MagicMock


# Mock I2C Bus
class MockI2CBus:
    def __init__(self):
        self.logger = MagicMock()
        self.mock_data = {
            "gyro": [0, 0, 0],
            "acc": [0, 0, 0],
        }

    def read_combined(self, low_addr, high_addr):
        return self.mock_data["gyro"][0]  # Return mocked gyro data

    def initialize_imu(self):
        return True  # Simulate successful initialization
