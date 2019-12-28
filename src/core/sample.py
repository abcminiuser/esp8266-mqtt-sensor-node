#          ESP-8266 Sensor Node
#      Released into the public domain.
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#

import machine


class SampleController:
    def __init__(self, interval, i2c_config):
        self.devices = []
        self.interval = interval

        if i2c_config:
            pin_sda = i2c_config['sda']
            pin_scl = i2c_config['scl']
            i2c_devices = i2c_config['devices']

            self.i2c = machine.I2C(sda=machine.Pin(pin_sda), scl=machine.Pin(pin_scl))

            for device_class, bus_address in i2c_devices:
                try:
                    sensor_device = device_class(bus_address, self.i2c)
                    sensor_device.sample()

                    self.devices.append(sensor_device)
                except OSError:
                    print("WARNING: {} failed to initialize at address {}!".format(
                        device_class.__name__, hex(bus_address)))

        else:
            self.i2c = None

    def scan_i2c(self):
        return self.i2c.scan() if self.i2c else []

    def sample(self):
        return [s.sample() for s in self.devices]
