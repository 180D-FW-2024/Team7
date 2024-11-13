class Pin:
    """
    Mock Pin class to simulate GPIO pins.
    """
    def __init__(self, pin_number, mode=None):
        self.pin_number = pin_number
        self.mode = mode

    def value(self, v=None):
        if v is None:
            return 0  # Simulate reading a pin value
        print(f"Set Pin {self.pin_number} to {v}")


class I2C:
    """
    Mock I2C class to simulate I2C communication.
    """
    def __init__(self, id, sda, scl, freq=100000):
        print(f"Mock I2C initialized: SDA={sda.pin_number}, SCL={scl.pin_number}, FREQ={freq}")
        self.devices = {}

    def writeto_mem(self, addr, register, data):
        print(f"Mock Write: Address={addr}, Register={register}, Data={data}")
        # Simulate writing data to a device register
        self.devices.setdefault(addr, {})[register] = data

    def readfrom_mem(self, addr, register, nbytes):
        print(f"Mock Read: Address={addr}, Register={register}, Bytes={nbytes}")
        # Simulate returning data from a register
        return self.devices.get(addr, {}).get(register, b'\x00' * nbytes)
