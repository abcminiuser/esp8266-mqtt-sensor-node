#          ESP-8266 Sensor Node
#      Released into the public domain.
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#

# Broadcom BMP280 Colour, Proximity and Gesture Sensor Driver.

import time


class APDS9960(object):
    DEFAULT_I2C_ADDR = 0x39

    REG_ENABLE = 0x80
    REG_CONFIG1 = 0x8F
    REG_CONFIG2 = 0x90
    REG_GCONFIG4 = 0xAB
    REG_GFLVL = 0xAE
    REG_GSTATUS = 0xAF
    REG_GFIFO_U = 0xFC
    REG_GFIFO_D = 0xFD
    REG_GFIFO_L = 0xFE
    REG_GFIFO_R = 0xFF

    MAX_GESTURE_SAMPLES = 32
    GESTURE_SENSITVITY = 20

    def __init__(self, i2c_addr, i2c_bus):
        self.addr = i2c_addr
        self.i2c = i2c_bus

        self.gesture_samples = [bytearray(4) for s in range(self.MAX_GESTURE_SAMPLES)]
        self.gesture_sample_count = 0

        self._reset()

    def _read_reg(self, address):
        buff = self.i2c.readfrom_mem(self.addr, address, 1)
        return buff[0]

    def _write_reg(self, address, value):
        buff = bytearray(1)
        buff[0] = value
        self.i2c.writeto_mem(self.addr, address, buff)

    def _reset(self):
        reg_config1 = (3 << 2) # PGAIN=3 (x8 gain)
        self._write_reg(self.REG_CONFIG1, reg_config1)

        reg_config2 = (3 << 4) # LBOOST=3 (x3 current)
        self._write_reg(self.REG_CONFIG2, reg_config2)

        reg_gconfig4 = (1 << 0) # GMODE=1
        self._write_reg(self.REG_GCONFIG4, reg_gconfig4)

        reg_enable = (1 << 6) | (1 << 5) | (1 << 3) # Enable gesture, proximity and wait engines
        self._write_reg(self.REG_ENABLE, reg_enable)

        reg_enable |= (1 << 0) # Power on
        self._write_reg(self.REG_ENABLE, reg_enable)

    def _buffer_samples(self):
        reg_gflvl = self._read_reg(self.REG_GFLVL)
        for i in range(reg_gflvl):
            if self.gesture_sample_count == self.MAX_GESTURE_SAMPLES:
                break

            self.i2c.readfrom_mem_into(self.addr, self.REG_GFIFO_U, self.gesture_samples[self.gesture_sample_count])
            self.gesture_sample_count += 1

        return reg_gflvl > 0

    def _process_samples(self):
        if self.gesture_sample_count < 4:
            return None

        udrl_first = [0, 0, 0, 0]
        udrl_last  = [0, 0, 0, 0]

        for i in range(self.gesture_sample_count):
            if all([s > 10 for s in self.gesture_samples[i]]):
                udrl_first = self.gesture_samples[i]
                break

        for i in reversed(range(self.gesture_sample_count)):
            if all([s > 10 for s in self.gesture_samples[i]]):
                udrl_last = self.gesture_samples[i]
                break

        self.gesture_sample_count = 0

        if all(udrl_first) and all(udrl_last):
            ud_ratio_first = (udrl_first[0] - udrl_first[1] * 100) / (udrl_first[0] + udrl_first[1])
            lr_ratio_first = (udrl_first[2] - udrl_first[3] * 100) / (udrl_first[2] + udrl_first[3])
            ud_ratio_last  = (udrl_last[0] - udrl_last[1] * 100) / (udrl_last[0] + udrl_last[1])
            lr_ratio_last  = (udrl_last[2] - udrl_last[3] * 100) / (udrl_last[2] + udrl_last[3])

            ud_delta = (ud_ratio_last - ud_ratio_first) / self.GESTURE_SENSITVITY
            lr_delta = (lr_ratio_last - lr_ratio_first) / self.GESTURE_SENSITVITY

            if abs(lr_delta) > 1:
                return "left_to_right" if lr_delta > 0 else "right_to_left"

            if abs(ud_delta) > 1:
                return "top_to_bottom" if ud_delta > 0 else "bottom_to_top"

        return None

    def read_gesture(self):
        reg_gstatus = self._read_reg(self.REG_GSTATUS)
        if reg_gstatus & (1 << 0) == 0: # Check gesture valid
            return None

        while self._buffer_samples():
            gesture = self._process_samples()
            if gesture is not None:
                return gesture

        return None

    def sample(self):
        gesture = self.read_gesture()
        if gesture is None:
            return None

        return {
            "apds9960/gesture": "{0}".format(gesture),
        }
