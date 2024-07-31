import time
from machine import UART, Pin
import json
from network_espnow import SensorBase

class SensorMHZ19PWM(SensorBase):
    def __init__(self):
        super().__init__()
    

    def send_sensor_data(self):
        data = {
            "topic": "sensor/co2",
            "value": "das"
        }
        data_str = json.dumps(data)
        self.e.send(self.peer_mac, data_str)
        print("Mensaje enviado:", data_str)
        time.sleep(2)