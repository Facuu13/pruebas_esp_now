import time
from config.network_espnow import SensorBase
import json
import machine

class ModuloReles(SensorBase):
    def __init__(self):
        super().__init__()
        # Configurar los pines de los relés 
        self.rele_pins = {
            1: machine.Pin(2, machine.Pin.OUT),  # Pin GPIO 2 para relé 1
            2: machine.Pin(32, machine.Pin.OUT),  # Pin GPIO 32 para relé 2
            3: machine.Pin(33, machine.Pin.OUT),  # Pin GPIO 33 para relé 3
            4: machine.Pin(25, machine.Pin.OUT)   # Pin GPIO 25 para relé 4
        }
        
        # Inicializar los estados de los relés
        self.rele_state_1 = False
        self.rele_state_2 = False
        self.rele_state_3 = False
        self.rele_state_4 = False
    
    def send_rele_state(self):
        for i in range(1, 5):
            data = {
                "topic": f"sensor/rele/state/{i}",
                "value": getattr(self, f"rele_state_{i}")  # Obtener el estado del relé
            }
            self.send_encrypted_data(data)
            print("Datos del sensor enviados:", data)

    def controlar_rele(self, rele_numero, estado):
        """
        Controla el relé especificado en base al número del relé y el estado proporcionado.
        """
        estado_new = str(estado).lower()
        if rele_numero in range(1, 5):
            if estado_new == "true":
                print(f"Prendiendo Relé {rele_numero}")
                setattr(self, f"rele_state_{rele_numero}", True)
                self.rele_pins[rele_numero].on()  # Encender el relé
            elif estado_new == "false":
                print(f"Apagando Relé {rele_numero}")
                setattr(self, f"rele_state_{rele_numero}", False)
                self.rele_pins[rele_numero].off()  # Apagar el relé
            else:
                print("Valor incorrecto")
            
            # Actualizar y enviar el estado del relé
            self.send_rele_state()
        else:
            print("Número de relé inválido")

# Instanciar la clase
reles = ModuloReles()
reles.send_rele_state()
