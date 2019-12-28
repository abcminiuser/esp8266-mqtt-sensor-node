#          ESP-8266 Sensor Node
#      Released into the public domain.
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#

from core.wifi import WIFIController
from core.mqtt import MQTTController
from core.sample import SampleController

from config import CONFIG

import time


def create_wifi_controller(wifi_config):
    ssid = wifi_config['ssid']
    passphrase = wifi_config['passphrase']

    return WIFIController(ssid, passphrase)


def create_mqtt_controller(mqtt_config, device_mac):
    mqtt_host = mqtt_config['host']
    mqtt_port = mqtt_config['port']
    device_id = mqtt_config['device_id'] or "esp8266_{}".format(device_mac)
    topic_prefix = mqtt_config['topic_prefix']

    return MQTTController(device_id, mqtt_host, mqtt_port, topic_prefix)


def create_sample_controller(sensor_config):
    sample_interval = sensor_config['sample_interval']
    i2c_config = sensor_config.get('i2c')

    return SampleController(sample_interval, i2c_config)


wifi_controller = create_wifi_controller(CONFIG['wifi'])
mqtt_controller = create_mqtt_controller(CONFIG['mqtt'], wifi_controller.mac_address)
sample_controller = create_sample_controller(CONFIG['sensors'])

found_i2c_devices = sample_controller.scan_i2c()
print("Found {} I2C devices at addresses: {}".format(
    len(found_i2c_devices), ' '.join(hex(x) for x in found_i2c_devices)))

while True:
    if not wifi_controller.connected:
        print("(Re-)connecting to '{}'...".format(wifi_controller.ssid))
        wifi_controller.connect()
        while not wifi_controller.connected:
            pass
        print("Connected to Wifi, IP address {}.".format(wifi_controller.current_ip))

        print("Connecting to MQTT server, host {}:{}...".format(
            mqtt_controller.host, mqtt_controller.port))
        mqtt_controller.connect()
        print("Connected to MQTT broker, device ID {}.".format(mqtt_controller.device_id))

    for sensor_sample in sample_controller.sample():
        if sensor_sample is None:
            continue

        for topic, value in sensor_sample.items():
            if value is None:
                continue

            sent_topic, sent_value = mqtt_controller.publish(topic, value)
            print("{} = {}".format(sent_topic, sent_value))

    time.sleep(sample_controller.interval)
