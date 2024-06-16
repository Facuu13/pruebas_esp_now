import network
import espnow
import time
import machine

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
sta.disconnect()      # For ESP8266

e = espnow.ESPNow()
e.active(True)
peer = b'\x58\xCF\x79\xE3\x6A\x70'   # MAC address of peer's wifi interface
e.add_peer(peer)      # Must add_peer() before send()

e.send(peer, "Starting...")
for i in range(100):
    e.send(peer, str(i), True)
    time.sleep(0.2)
    
e.send(peer, b'end')

# Configurar el ESP para despertar en 60 segundos y entrar en sueño profundo
#print("Entrando en modo de sueño profundo por 60 segundos...")
#machine.deepsleep(6000)
#debemos poner esta script en el boot para que se ejecute automaticamente en cada inicio
#porque el sueño profundo hace que se reinicie la placa
