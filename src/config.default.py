#          ESP-8266 Sensor Node
#      Released into the public domain.
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#

from sensors import BMP280
from sensors import SI7021


CONFIG = {
    'wifi': {
        # Wifi SSID and WPA2 Passphrase:
        'ssid': None, # (e.g. 'WiFi')
        'passphrase': None, # (e.g. 'Password')
    },

    'mqtt': {
        # MQTT server host address and port:
        'host': None, # (e.g. 'http://some-mqtt-server.example.com')
        'port': 1883,

        # Used in the MQTT topic, if None an auto-generated value will be used
        # from the device's MAC address (`esp8266_abcdef01`):
        'device_id': None, # (e.g. 'kitchen_sensors')

        # Root MQTT topic path, prefixed before device ID and sensor:
        'topic_prefix': None, # (e.g. 'home/esp8266')
    },

    'sensors': {
        # Seconds between sampling the configured sensors
        'sample_interval': 60,

        # I2C connected sensors (None if no I2C sensors used)
        'i2c': {
            # Pin connections for the I2C bus:
            'sda': 12, # (e.g. 12 for GPIO 12)
            'scl': 14, # (e.g. 14 for GPIO 14)

            # Sensors that are connected to the I2C bus, a list of class and
            # I2C bus address pairs
            'devices' : [
                (SI7021.SI7021, 0x40),
                (BMP280.BMP280, 0x76),
            ],
        },
    },
}
