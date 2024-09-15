import time
import json
from config.espnow_manager import ESPNowManager
from config.wifi_manager import WiFiManager
from config.mqtt_manager import MQTTManager
import http_server  


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
    espnow_manager.send_encrypted_data(data)
    print("Mensaje enviado:", data)


# Inicialización
wifi_manager = WiFiManager()
modo = wifi_manager.config.get("mode", "CL")

cliente_id = wifi_manager.config.get("cliente_id")
mqtt_broker = wifi_manager.config.get("mqtt_broker")
puerto = wifi_manager.config.get("puerto")
mqtt_user = wifi_manager.config.get("mqtt_user")
mqtt_pass = wifi_manager.config.get("mqtt_pass")

espnow_manager = ESPNowManager(peer_mac, mensaje_clave,modo_operacion=modo)

# Pasamos espnow_manager al servidor HTTP
http_server.set_espnow_manager(espnow_manager)

if modo == 'CL':
    mqtt_manager = MQTTManager(cliente_id, mqtt_broker, puerto, mqtt_user, mqtt_pass)
    mqtt_manager.set_callback(mensaje_callback)
    mqtt_manager.subscribe(topic_prueba)
    espnow_manager.set_mqtt_client(mqtt_manager) #permite el acceso al cliente mqtt desde espnow

# Iniciar servidor HTTP
http_server.start_server()  

while True:
    try:
        if modo == 'CL':
            mqtt_manager.check_msg()  # Revisa si hay mensajes nuevos
        time.sleep(1)  # Espera un poco antes de la siguiente verificación
    except Exception as e:
        print(f"Error al recibir mensajes: {e}")