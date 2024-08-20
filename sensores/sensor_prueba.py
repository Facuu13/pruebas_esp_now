import time
from config.network_espnow import SensorBase
import json

class SensorPrueba(SensorBase):
    def __init__(self):
        super().__init__()
        self.rele_state = False

    def send_sensor_data(self):
        data = {
                "topic": "sensor/prueba",
                "value": 2
            }
        data_str = json.dumps(data)
        self.e.send(self.peer_mac, data_str)
        print("Mensaje enviado:", data_str)
        time.sleep(1)
        data2 = {
                "topic": "sensor/rele/state",
                "value": self.rele_state
            }
        data_str2 = json.dumps(data2)
        self.e.send(self.peer_mac, data_str2)
        print("Mensaje enviado:", data_str2)
    
    def controlar_rele(self, estado):
        """
        Controla el relé (simulado) en base al estado proporcionado.
        """
        if estado == "on":
            print("Prendiendo Rele")
            self.rele_state = True
        elif estado == "off":
            print("Apangado rele")
            self.rele_state = False
        else:
            print("Valor incorrecto")
            
# from sensor_prueba import SensorPrueba
sensor = SensorPrueba()
# sensor.send_sensor_data()