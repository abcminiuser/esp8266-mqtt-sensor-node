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

from config import CONFIG


# WiFi Setup:
ssid = CONFIG['wifi']['ssid']
passphrase = CONFIG['wifi']['passphrase']

print("Connecting to '{}'...".format(ssid))
ap_if = network.WLAN(network.AP_IF)
sta_if = network.WLAN(network.STA_IF)

ap_if.active(False)
sta_if.active(True)

sta_if.connect(ssid, passphrase)
while not sta_if.isconnected():
    pass
print("Connected to Wifi, IP address {}.".format(sta_if.ifconfig()[0]))


# MQTT Init:
try:
    from umqtt.robust import MQTTClient
except ImportError:
    import upip
    upip.install('micropython-umqtt.robust')
    upip.install('micropython-umqtt.simple')

    from umqtt.robust import MQTTClient


# MQTT Broker Connection:
mqtt_host = CONFIG['mqtt']['host']
mqtt_port = CONFIG['mqtt']['port']
device_id = CONFIG['mqtt']['device_id']

if device_id is None:
    device_id = "esp8266_{}".format(ubinascii.hexlify(sta_if.config('mac')).decode())

print("Connecting to MQTT host, device ID '{}'...".format(device_id))
mqtt = MQTTClient(device_id, mqtt_host, mqtt_port)
mqtt.connect()
print("Connected to MQTT broker.")


# Sensor Setup:
sensor_devices = []

if CONFIG['sensors'].get('i2c'):
    pin_sda = CONFIG['sensors']['i2c']['sda']
    pin_scl = CONFIG['sensors']['i2c']['scl']
    i2c_devices = CONFIG['sensors']['i2c']['devices']

    i2c_bus = machine.I2C(sda=machine.Pin(pin_sda), scl=machine.Pin(pin_scl))

    print("Scanning I2C devices...")
    found_i2c_devices = i2c_bus.scan()
    print("Found I2C devices at addresses: {}".format(' '.join(hex(x) for x in found_i2c_devices)))

    for device_class, bus_address in i2c_devices:
        sensor_devices.append(device_class(bus_address, i2c_bus))


# Periodic Sensor Sampling:
topic_prefix = CONFIG['mqtt']['topic_prefix']
sample_interval = CONFIG['sensors']['sample_interval']

while True:
    sensor_samples = [s.sample() for s in sensor_devices]

    for sensor_sample in sensor_samples:
        if sensor_sample is None:
            continue

        for topic, value in sensor_sample.items():
            if value is None:
                continue

            topic_path = "{}/{}/{}".format(topic_prefix, device_id, topic)
            topic_value = value

            print("{} = {}".format(topic_path, topic_value))
            mqtt.publish(topic=topic_path, msg=topic_value)

    esp.sleep_type(esp.SLEEP_LIGHT)
    time.sleep(sample_interval)
    esp.sleep_type(esp.SLEEP_MODEM)
