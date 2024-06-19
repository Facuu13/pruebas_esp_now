# sensor_dht11.py
import machine
import dht
import time
from network_espnow import SensorBase

class SensorDHT11(SensorBase):
    def __init__(self, peer_mac):
        super().__init__(peer_mac)
        self.dht_pin = machine.Pin(32)
        self.dht_sensor = dht.DHT11(self.dht_pin)

    def send_sensor_data(self):
        try:
            self.dht_sensor.measure()
            temp = self.dht_sensor.temperature()
            hum = self.dht_sensor.humidity()
            message = "{};{}".format(temp, hum)
            self.e.send(self.peer_mac, message)
            print("Mensaje enviado:", message)
        except Exception as e:
            print("Error al enviar los datos del sensor:", e)

# from sensor_dht11 import SensorDHT11

# peer = b'\x58\xCF\x79\xE3\x6A\x70'  # MAC address of peer's wifi interface
# sensor = SensorDHT11(peer)
# sensor.send_sensor_data()  # Solo llama a send_sensor_data una vez



# Configurar el ESP para despertar en 60 segundos y entrar en sueño profundo
#print("Entrando en modo de sueño profundo por 60 segundos...")
#machine.deepsleep(6000)
#debemos poner esta script en el boot para que se ejecute automaticamente en cada inicio
#porque el sueño profundo hace que se reinicie la placa
