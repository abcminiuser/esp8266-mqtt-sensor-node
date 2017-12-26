import machine
import ubinascii
import time

from config import CONFIG
from sensors import SI7021


def setup_wlan(ssid, passphrase):
    import network

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, passphrase)

    return wlan

def setup_mqtt(host, port, device_id):
    from umqtt.robust import MQTTClient

    client = MQTTClient(device_id, host, port)
    client.connect()

    return client



print("Connecting to '{}'...".format(CONFIG['wifi']['ssid']))
wlan = setup_wlan(CONFIG['wifi']['ssid'], CONFIG['wifi']['passphrase'])
while not wlan.isconnected():
    machine.idle()
print("Connected to Wifi.")

device_id = CONFIG['mqtt'].get('device_id')
if device_id is None:
    device_id = "esp8266_{}".format(ubinascii.hexlify(wlan.config('mac')).decode())

print("Connecting to MQTT host, device ID '{}'...".format(device_id))
mqtt = setup_mqtt(CONFIG['mqtt']['host'], CONFIG['mqtt']['port'], device_id)
print("Connected to MQTT broker.")

print("Scanning I2C devices...")
i2c = machine.I2C(sda=machine.Pin(12), scl=machine.Pin(14)) # D5/D6 on silkscreen
found_i2c_devices = i2c.scan()
print("Found devices at addresses: {}".format(found_i2c_devices))

si7021 = SI7021.SI7021(0x40, i2c)

while True:
    mqtt.publish(topic="{}/{}/temperature".format(CONFIG['mqtt']['topic_prefix'], device_id), msg="{0:.2f}".format(si7021.readTemp()))
    time.sleep(5)
