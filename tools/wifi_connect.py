import time
import network

ssid = "quepasapatejode"
password = "losvilla08"

s = network.WLAN(network.STA_IF)
s.active(True)
s.connect(ssid, password)
while not s.isconnected():
    time.sleep(1)
    
print("Conectado a:", ssid)
print("Dirección IP:", s.ifconfig()[0])