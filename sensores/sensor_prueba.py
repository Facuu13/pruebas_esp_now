import time
from config.network_espnow import SensorBase
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
    
    def controlar_rele(self, estado):
        """
        Controla el relé (simulado) en base al estado proporcionado.
        """
        if estado == "on":
            print("Prendiendo Rele")
        elif estado == "off":
            print("Apangado rele")
        else:
            print("Valor incorrecto")
            
# from sensor_prueba import SensorPrueba
sensor = SensorPrueba()
# sensor.send_sensor_data()