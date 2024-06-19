import time
import machine
import dht
from network_espnow import wifi_reset, setup_espnow

dht_pin = machine.Pin(32)
dht_sensor = dht.DHT11(dht_pin)
peer = b'\x58\xCF\x79\xE3\x6A\x70'   # MAC address of peer's wifi interface

sta, ap = wifi_reset()
sta.config(channel=9)
e = setup_espnow(peer)

def send_sensor_data():
    dht_sensor.measure()
    temp = dht_sensor.temperature()
    hum = dht_sensor.humidity()
    message = "{};{}".format(temp, hum)
    e.send(peer, message)
    print("Mensaje enviado:", message)

send_sensor_data()


# Configurar el ESP para despertar en 60 segundos y entrar en sueño profundo
#print("Entrando en modo de sueño profundo por 60 segundos...")
#machine.deepsleep(6000)
#debemos poner esta script en el boot para que se ejecute automaticamente en cada inicio
#porque el sueño profundo hace que se reinicie la placa
