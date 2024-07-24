import time
import machine
import json
from network_espnow import SensorBase

class SensorMHZ19(SensorBase):
    def __init__(self, peer_mac):
        super().__init__(peer_mac)

    def send_sensor_data(self):
        for i in range(100):
            data = {
                "topic": "sensor/co2",
                "value": i
            }
            data_str = json.dumps(data)
            self.e.send(self.peer_mac, data_str)
            print("Mensaje enviado:", data_str)
            time.sleep(2)