import time

# Modified from https://gist.github.com/minyk/7c3070bc1c2766633b8ff1d4d51089cf

class SI7021(object):
    CMD_MEASURE_RELATIVE_HUMIDITY_HOLD_MASTER_MODE = 0xE5
    CMD_MEASURE_RELATIVE_HUMIDITY = 0xF5
    CMD_MEASURE_TEMPERATURE_HOLD_MASTER_MODE = 0xE3
    CMD_MEASURE_TEMPERATURE = 0xF3
    CMD_READ_TEMPERATURE_VALUE_FROM_PREVIOUS_RH_MEASUREMENT = 0xE0
    CMD_RESET = 0xFE
    CMD_WRITE_RH_T_USER_REGISTER_1 = 0xE6
    CMD_READ_RH_T_USER_REGISTER_1 = 0xE7
    CMD_WRITE_HEATER_CONTROL_REGISTER = 0x51
    CMD_READ_HEATER_CONTROL_REGISTER = 0x11

    def __init__(self, i2c_addr, i2c_bus):
        self.addr = i2c_addr
        self.cbuffer = bytearray(2)
        self.cbuffer[1] = 0x00
        self.i2c = i2c_bus

    def _write_command(self, command_byte):
        self.cbuffer[0] = command_byte
        self.i2c.writeto(self.addr, self.cbuffer)

    def _readTemp(self):
        self._write_command(self.CMD_MEASURE_TEMPERATURE)
        time.sleep_ms(25)
        temp = self.i2c.readfrom(self.addr, 3)
        temp2 = temp[0] << 8
        temp2 = temp2 | temp[1]
        return (175.72 * temp2 / 65536) - 46.85

    def _readRH(self):
        self._write_command(self.CMD_MEASURE_RELATIVE_HUMIDITY)
        time.sleep_ms(25)
        rh = self.i2c.readfrom(self.addr, 3)
        rh2 = rh[0] << 8
        rh2 = rh2 | rh[1]
        return (125 * rh2 / 65536) - 6

    def sample(self):
        return {
            "si7021/temperature": "{0:.1f}".format(self._readTemp()),
            "si7021/humidity": "{0:.1f}".format(self._readRH()),
        }
