#          ESP-8266 Sensor Node
#      Released into the public domain.
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#

import network
import ubinascii


class WIFIController:
    def __init__(self, ssid, passphrase):
        self.ap_if = network.WLAN(network.AP_IF)
        self.sta_if = network.WLAN(network.STA_IF)

        self.ssid = ssid
        self.passphrase = passphrase

    def connect(self):
        self.ap_if.active(False)
        self.sta_if.active(True)

        self.sta_if.connect(self.ssid, self.passphrase)

    @property
    def connected(self):
        return self.sta_if.isconnected()

    @property
    def mac_address(self):
        return ubinascii.hexlify(self.sta_if.config('mac')).decode()

    @property
    def current_ip(self):
        if not self.connected:
            return "0.0.0.0"

        interface_config = self.sta_if.ifconfig()
        return interface_config[0]
