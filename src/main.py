import network
import machine
import ubinascii
import time
import esp
from umqtt.robust import MQTTClient

from config import CONFIG
from sensors import SI7021


ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

print("Connecting to '{}'...".format(CONFIG['wifi']['ssid']))
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(CONFIG['wifi']['ssid'], CONFIG['wifi']['passphrase'])
while not sta_if.isconnected():
    machine.idle()
print("Connected to Wifi.")

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

si7021 = SI7021.SI7021(0x40, i2c)

while True:
    sensor_samples = si7021.sample()

    for topic, value in sensor_samples.items():
        mqtt.publish(topic="{}/{}/{}".format(CONFIG['mqtt']['topic_prefix'], device_id, topic), msg=value)

    esp.sleep_type(esp.SLEEP_LIGHT)
    time.sleep(CONFIG['sensors']['sample_interval'])
    esp.sleep_type(esp.SLEEP_MODEM)
