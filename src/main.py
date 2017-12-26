import network
import machine
import ubinascii
import time
from umqtt.robust import MQTTClient

from config import CONFIG
from sensors import SI7021



print("Connecting to '{}'...".format(CONFIG['wifi']['ssid']))
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(CONFIG['wifi']['ssid'], CONFIG['wifi']['passphrase'])
while not wlan.isconnected():
    machine.idle()
print("Connected to Wifi.")

device_id = CONFIG['mqtt'].get('device_id')
if device_id is None:
    device_id = "esp8266_{}".format(ubinascii.hexlify(wlan.config('mac')).decode())

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
    mqtt.publish(topic="{}/{}/temperature".format(CONFIG['mqtt']['topic_prefix'], device_id), msg="{0:.2f}".format(si7021.readTemp()))
    time.sleep(5)
