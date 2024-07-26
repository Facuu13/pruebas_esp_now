import time
import machine
import json
from network_espnow import SensorBase

class SensorLM35(SensorBase):
    def __init__(self):
        super().__init__()

    def send_sensor_data(self):
        for i in range(100):
            data = {
                "topic": "sensor/temp",
                "value": i
            }
            data_str = json.dumps(data)
            self.e.send(self.peer_mac, data_str)
            print("Mensaje enviado:", data_str)
            time.sleep(2)

# from sensor_lm35 import SensorLM35

# sensor = SensorLM35()
# sensor.send_sensor_data()  # Solo llama a send_sensor_data una vez

#enviar dato en forma de struct topic y dato

#por ahora no filtrar

#gateway llevar lista de mac conocidas
#cuando llegue una mac desconocida preguntar si queremos agregarlo o no