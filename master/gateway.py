import time
import json
from espnow_manager import ESPNowManager
from wifi_manager import WiFiManager
from mqtt_manager import MQTTManager
import http_server  


cliente_id = 'dispositivo1'
mqtt_broker = '192.168.1.11'
puerto = 1883
peer_mac = b'\xff' * 6
mensaje_clave = json.dumps({"respuesta": "canal_correcto"})
topic_prueba = b'/sensor/#'

def mensaje_callback(topic, msg):
    """
    Callback para manejar los mensajes recibidos en los tópicos suscritos.
    """
    print("Mensaje recibido en el tópico {}: {}".format(topic, msg))
    data = {
        "topic": topic,
        "value": msg
    }
    data_str = json.dumps(data)
    espnow_manager.send(peer_mac, data_str)
    print("Mensaje enviado:", data_str)


# Inicialización
wifi_manager = WiFiManager()
mqtt_manager = MQTTManager(cliente_id, mqtt_broker, puerto)
espnow_manager = ESPNowManager(peer_mac, mensaje_clave)

mqtt_manager.set_callback(mensaje_callback)
mqtt_manager.subscribe(topic_prueba)

espnow_manager.set_mqtt_client(mqtt_manager) #permite el acceso al cliente mqtt desde espnow

# Iniciar servidor HTTP
http_server.start_server()  

while True:
    try:
        mqtt_manager.check_msg()  # Revisa si hay mensajes nuevos
        time.sleep(1)  # Espera un poco antes de la siguiente verificación
    except Exception as e:
        print(f"Error al recibir mensajes: {e}")