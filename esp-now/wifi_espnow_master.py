import network
import espnow
import time

ssid = "quepasapatejode"
password = "losvilla08"

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

#callback
def recv_cb(e):
    while True:  # Leer todos los mensajes que esperan en el búfer
        mac, msg = e.irecv(0)  # No esperar si no hay mensajes
        if mac is None:
            return
        print(mac, msg)

sta, ap = wifi_reset()  # Reset wifi to AP off, STA on and disconnected
sta.connect(ssid, password)
while not sta.isconnected():  # Wait until connected...
    time.sleep(0.1)
    
sta.config(pm=sta.PM_NONE)  # ..then disable power saving
print("Proxy running on channel:", sta.config("channel"))
e = espnow.ESPNow(); e.active(True)
# Asignar la función de callback a ESP-NOW        
e.irq(recv_cb)