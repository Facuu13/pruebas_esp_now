import time
from config.network_espnow import SensorBase
import json
import machine

class ModuloReles(SensorBase):
    def __init__(self):
        super().__init__()
        self.rele_state = False
    
    def send_rele_state_encriptado(self):
        data = {
                "word" : "encriptado",
                "topic": "sensor/rele/state",
                "value": self.rele_state
            }
        data_str = json.dumps(data)
        self.e.send(self.peer_mac, data_str)
        print("Mensaje enviado:", data_str)


    def controlar_rele(self, estado):
        """
        Controla el relé (simulado) en base al estado proporcionado.
        """
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


reles = ModuloReles()