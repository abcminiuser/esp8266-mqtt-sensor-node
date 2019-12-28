#          ESP-8266 Sensor Node
#      Released into the public domain.
#
#   dean [at] fourwalledcubicle [dot] com
#         www.fourwalledcubicle.com
#


class MQTTController:
    def __init__(self, device_id, mqtt_host, mqtt_port, topic_prefix):
        self.host = mqtt_host
        self.port = mqtt_port

        self.device_id = device_id
        self.base_topic_path = "{}/{}".format(topic_prefix, device_id)

        self.client = None

    def _create_client(self):
        try:
            from umqtt.robust import MQTTClient
        except ImportError:
            import upip
            upip.install('micropython-umqtt.simple')
            upip.install('micropython-umqtt.robust')

            from umqtt.robust import MQTTClient

        return MQTTClient(self.device_id, self.host, self.port)

    def connect(self):
        if not self.client:
            self.client = self._create_client()

        self.client.connect()

    def publish(self, topic, value):
        if not self.client:
            return None

        path = "{}/{}".format(self.base_topic_path, topic)

        self.client.publish(topic=path, msg=value)
        return (path, value)
