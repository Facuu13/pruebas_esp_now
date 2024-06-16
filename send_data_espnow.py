import network
import espnow
import time
import machine
import dht

dht_pin = machine.Pin(32)
dht_sensor = dht.DHT11(dht_pin)

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
sta.disconnect()      # For ESP8266

e = espnow.ESPNow()
e.active(True)
peer = b'\x58\xCF\x79\xE3\x6A\x70'   # MAC address of peer's wifi interface
e.add_peer(peer)      # Must add_peer() before send()

def send_sensor_data():
    # Medir temperatura y humedad
    dht_sensor.measure()
    temp = dht_sensor.temperature()
    hum = dht_sensor.humidity()
    
    # Crear mensaje con la temperatura y la humedad
    message = "Temp: {}C, Hum: {}%".format(temp, hum)
    
    # Enviar mensaje
    e.send(peer, message)
    print("Mensaje enviado:", message)


send_sensor_data()


# Configurar el ESP para despertar en 60 segundos y entrar en sueño profundo
#print("Entrando en modo de sueño profundo por 60 segundos...")
#machine.deepsleep(6000)
#debemos poner esta script en el boot para que se ejecute automaticamente en cada inicio
#porque el sueño profundo hace que se reinicie la placa
