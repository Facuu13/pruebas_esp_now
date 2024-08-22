import time
from config.network_espnow import SensorBase
import json
import machine

class SensorPrueba(SensorBase):
    def __init__(self):
        super().__init__()
        self.rele_state = False

    def send_sensor_data_encriptado(self):
        if self.enable_sensor: #sensor habilitado
            data = {
                    "word" : "encriptado",
                    "topic": "sensor/prueba",
                    "value": 2
                }
            data_str = json.dumps(data)
            self.e.send(self.peer_mac, data_str)
            print("Mensaje enviado:", data_str)
            time.sleep(1)
        else:
            print("sensor deshabilitado")

    def send_rele_state_encriptado(self):
        if self.enable_sensor: #sensor habilitado
            data2 = {
                    "word" : "encriptado",
                    "topic": "sensor/rele/state",
                    "value": self.rele_state
                }
            data_str2 = json.dumps(data2)
            self.e.send(self.peer_mac, data_str2)
            print("Mensaje enviado:", data_str2)
        else:
            print("sensor deshabilitado")
    
    def controlar_rele(self, estado):
        """
        Controla el relé (simulado) en base al estado proporcionado.
        """
        if self.enable_sensor:
            if estado == "true":
                print("Prendiendo Rele")
                self.rele_state = True
                self.send_rele_state_encriptado() #actualizamos el estado del rele
            elif estado == "false":
                print("Apangado rele")
                self.rele_state = False
                self.send_rele_state_encriptado() #actualizamos el estado del rele
            else:
                print("Valor incorrecto")
        else:
            print("sensor deshabilitado")

#actualizar el estado 

# from sensor_prueba import SensorPrueba
sensor = SensorPrueba()
sensor.send_sensor_data_encriptado()

print("entrando en modo sleep")
# 10000 = 10 segundos
sleep_time = 20000 # 20seg
machine.deepsleep(sleep_time)