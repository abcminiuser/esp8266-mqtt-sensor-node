#          ESP-8266 Sensor Node
#      Released into the public domain.
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#

# Bosch BMP280 Pressure Sensor Driver.

import time


class BMP280(object):
    REG_RESET     = 0xE0
    REG_STATUS    = 0xF3
    REG_CONTROL   = 0xF4
    REG_PRES_MSB  = 0xF7
    REG_PRES_LSB  = 0xF8
    REG_PRES_XLSB = 0xF9
    REG_TEMP_MSB  = 0xFA
    REG_TEMP_LSB  = 0xFB
    REG_TEMP_XLSB = 0xFC

    REG_CALIB = {
        'T1' : {'addr': 0x88, 'signed': False},
        'T2' : {'addr': 0x8A, 'signed': True },
        'T3' : {'addr': 0x8C, 'signed': True },
        'P1' : {'addr': 0x8E, 'signed': False},
        'P2' : {'addr': 0x90, 'signed': True },
        'P3' : {'addr': 0x92, 'signed': True },
        'P4' : {'addr': 0x94, 'signed': True },
        'P5' : {'addr': 0x96, 'signed': True },
        'P6' : {'addr': 0x98, 'signed': True },
        'P7' : {'addr': 0x9A, 'signed': True },
        'P8' : {'addr': 0x9C, 'signed': True },
        'P9' : {'addr': 0x9E, 'signed': True },
    }


    def __init__(self, i2c_addr, i2c_bus):
        self.addr = i2c_addr
        self.i2c = i2c_bus

        self._reset()
        self.cal = self._load_calibration()


    def _load_calibration(self):
        cal_values = dict()

        for reg_name, reg_attr in self.REG_CALIB.items():
            cal_value_raw = self.i2c.readfrom_mem(self.addr, reg_attr['addr'], 2)
            cal_values[reg_name] = cal_value_raw[0] | (cal_value_raw[1] << 8)

            if reg_attr['signed']:
                if cal_values[reg_name] > 0x7FFF:
                    cal_values[reg_name] -= 0x10000

        return cal_values


    def _reset(self):
        reset = bytearray(1)
        reset[0] = 0xB6 # Reset magic byte, from datasheet
        self.i2c.writeto_mem(self.addr, self.REG_RESET, reset)


    def _read_raw(self):
        control = bytearray(1)
        control[0] = (0b01 << 0) | (0b101 << 2) | (0b010 << 5) # Force single sample, x16 pressure oversample, x2 temperature oversample
        self.i2c.writeto_mem(self.addr, self.REG_CONTROL, control)

        while True:
            status = self.i2c.readfrom_mem(self.addr, self.REG_STATUS, 1)
            if status[0] & (1 << 3) == 0: # Check if sensor is still sampling
                break
            else:
                time.sleep_ms(2)

        raw_temp_bytes = self.i2c.readfrom_mem(self.addr, self.REG_TEMP_MSB, 3)
        raw_temp = raw_temp_bytes[0] << 16 | raw_temp_bytes[1] << 8 | raw_temp_bytes[2]

        raw_pressure_bytes = self.i2c.readfrom_mem(self.addr, self.REG_PRES_MSB, 3)
        raw_pressure = raw_pressure_bytes[0] << 16 | raw_pressure_bytes[1] << 8 | raw_pressure_bytes[2]

        return (raw_temp, raw_pressure)


    def _calculate_t_fine(self, raw_temp):
        dig_T1 = self.cal['T1']
        dig_T2 = self.cal['T2']
        dig_T3 = self.cal['T3']

        # Convert 24-bit oversampled value to 20-bit
        adc_T = raw_temp >> 4

        # Conversion code from the BMP280 datasheet:
        var1 = ((((adc_T >> 3) - (dig_T1 << 1))) * dig_T2) >> 11;
        var2 = (((((adc_T >> 4) - dig_T1) * ((adc_T >> 4) - dig_T1)) >> 12) * dig_T3) >> 14;
        t_fine = var1 + var2;

        return t_fine


    def _calculate_temperature(self, t_fine):
        # Conversion code from the BMP280 datasheet:
        T = (t_fine * 5 + 128) >> 8;

        return T / 100.0


    def _calculate_pressure(self, t_fine, raw_pressure):
        dig_P1 = self.cal['P1']
        dig_P2 = self.cal['P2']
        dig_P3 = self.cal['P3']
        dig_P4 = self.cal['P4']
        dig_P5 = self.cal['P5']
        dig_P6 = self.cal['P6']
        dig_P7 = self.cal['P7']
        dig_P8 = self.cal['P8']
        dig_P9 = self.cal['P9']

        # Convert 24-bit oversampled value to 20-bit
        adc_P = raw_pressure >> 4

        # Conversion code from the BMP280 datasheet:
        var1 = t_fine - 128000;
        var2 = var1 * var1 * dig_P6;
        var2 = var2 + ((var1 * dig_P5) << 17);
        var2 = var2 + (dig_P4 << 35);
        var1 = ((var1 * var1 * dig_P3) >> 8) + ((var1 * dig_P2) << 12);
        var1 = ((1 << 47) + var1) * dig_P1 >> 33;
        if var1 == 0:
            return 0

        p = 1048576 - adc_P;
        p = int((((p << 31) - var2) * 3125) / var1);
        var1 = (dig_P9 * (p >> 13) * (p >> 13)) >> 25;
        var2 = (dig_P8 * p) >> 19;
        p = ((p + var1 + var2) >> 8) + (dig_P7 <<4);

        return p / 256


    def read_tempressure(self):
        (raw_temp, raw_pressure) = self._read_raw();
        t_fine = self._calculate_t_fine(raw_temp)

        return self._calculate_temperature(t_fine)


    def read_pressure(self):
        (raw_temp, raw_pressure) = self._read_raw();
        t_fine = self._calculate_t_fine(raw_temp)

        return self._calculate_pressure(t_fine, raw_pressure)


    def read_temperature_pressure(self):
        (raw_temp, raw_pressure) = self._read_raw();
        t_fine = self._calculate_t_fine(raw_temp)

        temperature = self._calculate_temperature(t_fine)
        pressure = self._calculate_pressure(t_fine, raw_pressure)

        return (temperature, pressure)


    def sample(self):
        (temperature, pressure) = self.read_temperature_pressure()

        return {
            "bmp280/temperature": "{0:.1f}".format(temperature),
            "bmp280/pressure": "{0:.1f}".format(pressure),
        }
