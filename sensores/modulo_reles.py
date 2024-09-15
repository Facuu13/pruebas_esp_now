import time
from config.network_espnow import SensorBase
import json
import machine

class ModuloReles(SensorBase):
    def __init__(self):
        super().__init__()
        self.rele_state_1 = False
        self.rele_state_2 = False
        self.rele_state_3 = False
        self.rele_state_4 = False
    
    def send_rele_state(self):
        for i in range(1, 5):
            data = {
                "topic": f"sensor/rele/state/{i}",
                "value": getattr(self, f"rele_state_{i}") #obtenemos el valor del estado del rele
            }
            self.send_encrypted_data(data)
            print("Datos del sensor enviados:", data)


    def controlar_rele(self, rele_numero, estado):
        """
        Controla el relé especificado en base al número del relé y el estado proporcionado.
        """
        if rele_numero in range(1, 5):
            if estado == "True" or "true":
                print(f"Prendiendo Rele {rele_numero}")
                setattr(self, f"rele_state_{rele_numero}", True)
            elif estado == "False" or "false":
                print(f"Apagando Rele {rele_numero}")
                setattr(self, f"rele_state_{rele_numero}", False)
            else:
                print("Valor incorrecto")
            self.send_rele_state()  # Actualiza y envía el estado del relé
        else:
            print("Número de relé inválido")


reles = ModuloReles()