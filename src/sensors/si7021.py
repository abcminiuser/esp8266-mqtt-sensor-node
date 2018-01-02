#          ESP-8266 Sensor Node
#      Released into the public domain.
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#

# Silicon Labs SI7021 Temperature/Humidity Sensor Driver.

import time


class SI7021(object):
    def __init__(self, i2c_addr, i2c_bus):
        self.addr = i2c_addr
        self.i2c = i2c_bus

    def read_temperature(self):
        command = bytearray(1)
        command[0] = 0xF3
        self.i2c.writeto(self.addr, command)

        for i in range(0, 10):
            try:
                result = self.i2c.readfrom(self.addr, 2)
            except OSError:
                time.sleep_ms(2)

        if result is None:
            return None

        temp_raw = result[0] << 8 | result[1]

        # Conversion code from the SI7021 datasheet:
        T = (175.72 * temp_raw) / 65536 - 46.85

        return T

    def read_relative_humidity(self):
        command = bytearray(1)
        command[0] = 0xF5
        self.i2c.writeto(self.addr, command)

        for i in range(0, 10):
            try:
                result = self.i2c.readfrom(self.addr, 2)
            except OSError:
                time.sleep_ms(2)

        if result is None:
            return None

        humidity_raw = result[0] << 8 | result[1]

        # Conversion code from the SI7021 datasheet:
        rH = (125 * humidity_raw) / 65536 - 6

        return rH

    def sample(self):
        return {
            "si7021/temperature": "{0:.1f}".format(self.read_temperature()),
            "si7021/humidity": "{0:.1f}".format(self.read_relative_humidity()),
        }
