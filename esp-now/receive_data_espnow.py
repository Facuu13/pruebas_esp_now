import network
import espnow

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()   

e = espnow.ESPNow()
e.active(True)

#callback
def recv_cb(e):
    while True:  # Leer todos los mensajes que esperan en el búfer
        mac, msg = e.irecv(0)  # No esperar si no hay mensajes
        if mac is None:
            return
        print(mac, msg)

# Asignar la función de callback a ESP-NOW        
e.irq(recv_cb)