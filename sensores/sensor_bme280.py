import time
import machine
from network_espnow import wifi_reset, setup_espnow

peer = b'\x58\xCF\x79\xE3\x6A\x70'   # MAC address of peer's wifi interface

sta, ap = wifi_reset()
sta.config(channel=9)
e = setup_espnow(peer)

def send_sensor_data():
    for i in range(100):
        e.send(peer, str(i))
        print("Mensaje enviado:", i)
        time.sleep(2)

send_sensor_data()