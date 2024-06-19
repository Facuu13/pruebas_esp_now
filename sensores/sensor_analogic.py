import network
import espnow
import time
import machine


def wifi_reset():   # Reset wifi to AP_IF off, STA_IF on and disconnected
    sta = network.WLAN(network.STA_IF); sta.active(False)
    ap = network.WLAN(network.AP_IF); ap.active(False)
    sta.active(True)
    while not sta.active():
        time.sleep(0.1)
    sta.disconnect()   # For ESP8266
    while sta.isconnected():
        time.sleep(0.1)
    return sta, ap

def send_sensor_data():

    for i in range (100):
    # Enviar mensaje
        e.send(peer, str(i))
        print("Mensaje enviado:", i)
        time.sleep(2)

sta, ap = wifi_reset()   # Reset wifi to AP off, STA on and disconnected
sta.config(channel=9)    #poner el canal del servidor
peer = b'\x58\xCF\x79\xE3\x6A\x70'   # MAC address of peer's wifi interface
e = espnow.ESPNow()
e.active(True)
e.add_peer(peer)      # Must add_peer() before send()

send_sensor_data()