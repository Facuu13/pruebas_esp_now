import time
from config.network_espnow import SensorBase
import json
import machine

modelo = 'DHT11'

class SensorPrueba(SensorBase):
    def __init__(self):
        super().__init__()

    def send_sensor_data(self, dato):
        """
        Enviar datos del sensor cifrados.
        """
        data = {
            "topic": "sensor/prueba",
            "value": dato,
            "modelo": modelo
        }

        # Utilizamos el método general de la clase base para cifrar y enviar los datos
        self.send_encrypted_data(data)
        print("Datos del sensor enviados:", data)




#actualizar el estado 

# from sensor_prueba import SensorPrueba
sensor = SensorPrueba()

# print("entrando en modo sleep")
# # 10000 = 10 segundos
# sleep_time = 20000 # 20seg
# machine.deepsleep(sleep_time)