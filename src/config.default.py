CONFIG = {
    'wifi': {
        # Wifi SSID and WPA2 Passphrase:
        'ssid': None, # (e.g. 'WiFi')
        'passphrase': None, # (e.g. 'Password')
    },

    'mqtt': {
        # MQTT server host address and port:
        'host': None, # (e.g. 'http://some-mqtt-server.example.com)
        'port': 1883,

        # Used in the MQTT topic, if None an auto-generated value will be used
        # from the device's MAC address:
        'device_id': None, # (e.g. 'kitchen_sensors')

        # Root MQTT topic path, prefixed before device ID and sensor:
        'topic_prefix': None, # (e.g. 'home/esp8266')
    },
}
