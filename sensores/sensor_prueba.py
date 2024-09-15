import time
from config.network_espnow import SensorBase
import json
import machine

class SensorPrueba(SensorBase):
    def __init__(self):
        super().__init__()

    def send_sensor_data_encriptado(self,dato):
        data = {
                "topic": "sensor/prueba",
                "value": dato
            }
        data_str = json.dumps(data)
        self.e.send(self.peer_mac, data_str)
        print("Mensaje enviado:", data_str)
        time.sleep(1)




#actualizar el estado 

# from sensor_prueba import SensorPrueba
sensor = SensorPrueba()

# print("entrando en modo sleep")
# # 10000 = 10 segundos
# sleep_time = 20000 # 20seg
# machine.deepsleep(sleep_time)