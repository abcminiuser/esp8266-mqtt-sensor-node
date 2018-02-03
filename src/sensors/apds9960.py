#          ESP-8266 Sensor Node
#      Released into the public domain.
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#

# Broadcom APDS9960 Colour, Proximity and Gesture Sensor Driver.

# Core design from the Sparkfun library (https://github.com/sparkfun/SparkFun_APDS-9960_Sensor_Arduino_Library)


class APDS9960(object):
    DEFAULT_I2C_ADDR = 0x39

    REG_ENABLE = 0x80
    REG_ATIME = 0x81
    REG_WTIME = 0x83
    REG_AILTL = 0x84
    REG_AILTH = 0x85
    REG_AIHTL = 0x86
    REG_AIHTH = 0x87
    REG_PILT = 0x89
    REG_PIHT = 0x8B
    REG_PERS = 0x8C
    REG_CONFIG1 = 0x8D
    REG_PPULSE = 0x8E
    REG_CONTROL = 0x8F
    REG_CONFIG2 = 0x90
    REG_ID = 0x92
    REG_STATUS = 0x93
    REG_CDATAL = 0x94
    REG_CDATAH = 0x95
    REG_RDATAL = 0x96
    REG_RDATAH = 0x97
    REG_GDATAL = 0x98
    REG_GDATAH = 0x99
    REG_BDATAL = 0x9A
    REG_BDATAH = 0x9B
    REG_PDATA = 0x9C
    REG_POFFSET_UR = 0x9D
    REG_POFFSET_DL = 0x9E
    REG_CONFIG3 = 0x9F
    REG_GPENTH = 0xA0
    REG_GEXTH = 0xA1
    REG_GCONF1 = 0xA2
    REG_GCONF2 = 0xA3
    REG_GOFFSET_U = 0xA4
    REG_GOFFSET_D = 0xA5
    REG_GOFFSET_L = 0xA7
    REG_GOFFSET_R = 0xA9
    REG_GPULSE = 0xA6
    REG_GCONF3 = 0xAA
    REG_GCONF4 = 0xAB
    REG_GFLVL = 0xAE
    REG_GSTATUS = 0xAF
    REG_IFORCE = 0xE4
    REG_PICLEAR = 0xE5
    REG_CICLEAR = 0xE6
    REG_AICLEAR = 0xE7
    REG_GFIFO_U = 0xFC
    REG_GFIFO_D = 0xFD
    REG_GFIFO_L = 0xFE
    REG_GFIFO_R = 0xFF

    MAX_GESTURE_SAMPLES = 32

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
        reg_enable = 0  # Power off
        self._write_reg(self.REG_ENABLE, reg_enable)

        reg_atime = 219
        self._write_reg(self.REG_ATIME, reg_atime)

        reg_wtime = 246
        self._write_reg(self.REG_WTIME, reg_wtime)

        reg_ppulse = 0x89
        self._write_reg(self.REG_PPULSE, reg_ppulse)

        reg_config1 = 0x60
        self._write_reg(self.REG_CONFIG1, reg_config1)

        reg_config2 = (3 << 4)  # LBOOST=3 (x3 current)
        self._write_reg(self.REG_CONFIG2, reg_config2)

        reg_gpulse = 0xc9
        self._write_reg(self.REG_GPULSE, reg_gpulse)

        reg_pilt = 0
        self._write_reg(self.REG_PILT, reg_pilt)

        reg_piht = 50
        self._write_reg(self.REG_PIHT, reg_piht)

        reg_gpenth = 40
        self._write_reg(self.REG_GPENTH, reg_gpenth)

        reg_gexth = 30
        self._write_reg(self.REG_GEXTH, reg_gexth)

        reg_enable = (1 << 0)  # Power on
        self._write_reg(self.REG_ENABLE, reg_enable)

        reg_enable |= (1 << 6) | (1 << 3) | (1 << 2)  # Enable gesture, wait and proximity engines
        self._write_reg(self.REG_ENABLE, reg_enable)

    def _buffer_samples(self):
        reg_gflvl = self._read_reg(self.REG_GFLVL)
        for i in range(reg_gflvl):
            if self.gesture_sample_count == self.MAX_GESTURE_SAMPLES:
                break

            self.i2c.readfrom_mem_into(self.addr, self.REG_GFIFO_U,
                                       self.gesture_samples[self.gesture_sample_count])
            self.gesture_sample_count += 1

        return reg_gflvl > 0

    def _process_samples(self):
        if self.gesture_sample_count < 4:
            return None

        udrl_first = [0, 0, 0, 0]
        udrl_last = [0, 0, 0, 0]

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
            ud_ratio_last = (udrl_last[0] - udrl_last[1] * 100) / (udrl_last[0] + udrl_last[1])
            lr_ratio_last = (udrl_last[2] - udrl_last[3] * 100) / (udrl_last[2] + udrl_last[3])

            ud_delta = (ud_ratio_last - ud_ratio_first)
            lr_delta = (lr_ratio_last - lr_ratio_first)

            if abs(lr_delta) > 1:
                return "left_to_right" if lr_delta > 0 else "right_to_left"

            if abs(ud_delta) > 1:
                return "top_to_bottom" if ud_delta > 0 else "bottom_to_top"

        return None

    def read_gesture(self):
        reg_gstatus = self._read_reg(self.REG_GSTATUS)
        if reg_gstatus & (1 << 0) == 0:  # Check gesture valid
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
