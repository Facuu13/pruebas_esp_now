import time
import machine
from network_espnow import SensorBase

class SensorLM35(SensorBase):
    def __init__(self, peer_mac):
        super().__init__(peer_mac)

    def send_sensor_data(self):
        for i in range(100):
            self.e.send(self.peer_mac, str(i))
            print("Mensaje enviado:", i)
            time.sleep(2)

# from sensor_lm35 import SensorLM35

# peer = b'\x58\xCF\x79\xE3\x6A\x70'  # MAC address of peer's wifi interface
# sensor = SensorLM35(peer)
# sensor.send_sensor_data()  # Solo llama a send_sensor_data una vez

#enviar dato en forma de struct topic y dato

#por ahora no filtrar

#gateway llevar lista de mac conocidas
#cuando llegue una mac desconocida preguntar si queremos agregarlo o no