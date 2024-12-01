import time
import json
from config.espnow_manager import ESPNowManager
from config.wifi_manager import WiFiManager
from config.mqtt_manager import MQTTManager
import http_server 

import uasyncio as asyncio


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

def mensaje_reinicio():
    data = {
        "palabra_clave": "reiniciar",
    }
    espnow_manager.send_encrypted_data(data)
    #print("Mensaje enviado:", data)

# Inicialización
wifi_manager = WiFiManager()
modo = wifi_manager.config.get("mode")
conectado_a_internet = wifi_manager.conectado_wifi

if modo == 'CL' and conectado_a_internet:
    cliente_id = wifi_manager.config.get("cliente_id")
    mqtt_broker = wifi_manager.config.get("mqtt_broker")
    puerto = wifi_manager.config.get("puerto")
    mqtt_user = wifi_manager.config.get("mqtt_user")
    mqtt_pass = wifi_manager.config.get("mqtt_pass")
    espnow_manager = ESPNowManager(peer_mac, mensaje_clave,modo,wifi_manager)
    mqtt_manager = MQTTManager(cliente_id, mqtt_broker, puerto, mqtt_user, mqtt_pass)
    mqtt_manager.set_callback(mensaje_callback)
    mqtt_manager.subscribe(topic_prueba)
    espnow_manager.set_mqtt_client(mqtt_manager) #permite el acceso al cliente mqtt desde espnow
elif modo == 'AP':
    espnow_manager = ESPNowManager(peer_mac, mensaje_clave,modo,wifi_manager)
else:
    espnow_manager = ESPNowManager(peer_mac, mensaje_clave,'AP',wifi_manager)

hora_actual=wifi_manager.devolver_hora_actual()
print(f"Fecha y hora: {hora_actual}")

mensaje_reinicio() #reiniciamos los nodos 

# Pasamos espnow_manager al servidor HTTP
http_server.set_espnow_manager(espnow_manager)

# Iniciar servidor HTTP
http_server.start_server()


while True:
    try:
        if modo == 'CL' and conectado_a_internet:
            mqtt_manager.check_msg()  # Revisa si hay mensajes nuevos
        time.sleep(1)  # Espera un poco antes de la siguiente verificación
    except Exception as e:
        print(f"Error al recibir mensajes: {e}")



# async def mqtt_loop():
#     while True:
#         mqtt_manager.check_msg()  # Revisa si hay mensajes nuevos
#         await asyncio.sleep(1)    # Espera sin bloquear otras tareas

# async def main():

#     # Si estás en modo CL, también ejecuta el loop MQTT en paralelo
#     if modo == 'CL' and conectado_a_internet:
#         asyncio.create_task(mqtt_loop())

#     while True:
#         await asyncio.sleep(1)  # Mantiene el loop principal activo

# # Ejecuta el loop principal de asyncio
# asyncio.run(main())

