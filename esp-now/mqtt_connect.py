from umqtt.simple import MQTTClient
import time
import network
import machine
import ujson

ssid = "quepasapatejode"
password = "losvilla08"
# Configuración del cliente MQTT
cliente_id = 'dispositivo1'
mqtt_broker = '192.168.1.11'
puerto = 1883

s = network.WLAN(network.STA_IF)
s.active(True)
s.connect(ssid, password)
while not s.isconnected():
    time.sleep(1)
    
print("Conectado a:", ssid)
print("Dirección IP:", s.ifconfig()[0])

def conectar_mqtt(cliente_id, mqtt_broker, puerto):
    cliente = MQTTClient(cliente_id, mqtt_broker, port=puerto)
    try:
        cliente.connect()
        print("Conectado al broker MQTT")
    except Exception as e:
        print(f"Error al conectar al broker MQTT: {e}")
    return cliente

cliente = conectar_mqtt(cliente_id, mqtt_broker, puerto)