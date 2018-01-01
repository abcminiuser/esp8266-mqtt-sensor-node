#          ESP-8266 Sensor Node
#      Released into the public domain.
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#


import network
import machine
import ubinascii
import time
import esp
from umqtt.robust import MQTTClient

from config import CONFIG
from sensors import BMP280
from sensors import SI7021


ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

print("Connecting to '{}'...".format(CONFIG['wifi']['ssid']))
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(CONFIG['wifi']['ssid'], CONFIG['wifi']['passphrase'])
while not sta_if.isconnected():
    pass
print("Connected to Wifi, IP address {}.".format(sta_if.ifconfig()[0]))

device_id = CONFIG['mqtt'].get('device_id')
if device_id is None:
    device_id = "esp8266_{}".format(ubinascii.hexlify(sta_if.config('mac')).decode())

print("Connecting to MQTT host, device ID '{}'...".format(device_id))
mqtt = MQTTClient(device_id, CONFIG['mqtt']['host'], CONFIG['mqtt']['port'])
mqtt.connect()
print("Connected to MQTT broker.")

print("Scanning I2C devices...")
i2c = machine.I2C(sda=machine.Pin(12), scl=machine.Pin(14)) # D5/D6 on silkscreen
found_i2c_devices = i2c.scan()
print("Found I2C devices at addresses: {}".format(' '.join(hex(x) for x in found_i2c_devices)))

sensor_devices = [
    SI7021.SI7021(0x40, i2c),
    BMP280.BMP280(0x76, i2c)
]

while True:
    sensor_samples = [s.sample() for s in sensor_devices]

    for sensor_sample in sensor_samples:
        for topic, value in sensor_sample.items():
            topic_path  = "{}/{}/{}".format(CONFIG['mqtt']['topic_prefix'], device_id, topic)
            topic_value = value

            print("{} = {}".format(topic_path, topic_value))
            mqtt.publish(topic=topic_path, msg=topic_value)

    esp.sleep_type(esp.SLEEP_LIGHT)
    time.sleep(CONFIG['sensors']['sample_interval'])
    esp.sleep_type(esp.SLEEP_MODEM)
