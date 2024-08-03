import time
import machine
from network_espnow import SensorBase
import json

class SensorPrueba(SensorBase):
    def __init__(self):
        super().__init__()

    def send_sensor_data(self):
        for i in range(100):
            data = {
                    "topic": "sensor/prueba",
                    "value": i
                }
            data_str = json.dumps(data)
            self.e.send(self.peer_mac, data_str)
            print("Mensaje enviado:", data_str)
            time.sleep(1)
            
# from sensor_prueba import SensorPrueba
sensor = SensorPrueba()
# sensor.send_sensor_data()