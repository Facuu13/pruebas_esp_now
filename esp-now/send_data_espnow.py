import network
import espnow
import time
import machine
import dht


dht_pin = machine.Pin(32)
dht_sensor = dht.DHT11(dht_pin)


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
    # Medir temperatura y humedad
    dht_sensor.measure()
    temp = dht_sensor.temperature()
    hum = dht_sensor.humidity()
    
    # Crear mensaje con la temperatura y la humedad
    message = "Temp: {}C, Hum: {}%".format(temp, hum)
    
    # Enviar mensaje
    e.send(peer, message)
    print("Mensaje enviado:", message)

sta, ap = wifi_reset()   # Reset wifi to AP off, STA on and disconnected
sta.config(channel=10)    #poner el canal del servidor
peer = b'\x58\xCF\x79\xE3\x6A\x70'   # MAC address of peer's wifi interface
e = espnow.ESPNow()
e.active(True)
e.add_peer(peer)      # Must add_peer() before send()

send_sensor_data()


# Configurar el ESP para despertar en 60 segundos y entrar en sueño profundo
#print("Entrando en modo de sueño profundo por 60 segundos...")
#machine.deepsleep(6000)
#debemos poner esta script en el boot para que se ejecute automaticamente en cada inicio
#porque el sueño profundo hace que se reinicie la placa
