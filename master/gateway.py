import time
import json
from espnow_manager import ESPNowManager
from wifi_manager import WiFiManager
from mqtt_manager import MQTTManager
import socket
from micropython import alloc_emergency_exception_buf

SSID = "quepasapatejode"
PASSWORD = "losvilla08"
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

def handle_root():
    return b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHello, World!"

def handle_status():
        return b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nStatus: OK"

def handle_not_found():
    return b"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nNot Found"

def handle_client(cl):
    try:
        request = cl.recv(1024)  # Recibe la petición del cliente
        request_lines = request.split(b'\r\n')
        request_line = request_lines[0]
        method, path, _ = request_line.split(b' ')

        if method == b'GET':
            if path == b'/':
                response = handle_root()
            elif path == b'/status':
                response = handle_status()
            else:
                response = handle_not_found()
        else:
            response = b"HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/plain\r\n\r\nMethod Not Allowed"

        cl.send(response)  # Envía la respuesta al cliente
    except Exception as e:
        print(f"Error manejando la solicitud: {e}")
    finally:
        cl.close()  # Cierra la conexión con el cliente

def accept_client(server_sock):
        try:
            cl, addr = server_sock.accept()  # Acepta una conexión entrante
            print('Client connected from', addr)
            # Registra el manejador para la conexión del cliente
            cl.setsockopt(socket.SOL_SOCKET, 20,
                        lambda x: handle_client(x))
        except Exception as e:
            print("Exception accepting client:")

def start_server():
        # Obtiene la dirección IP y el puerto
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        server_sock = socket.socket()  # Crea el socket del servidor
        # Permite reutilizar la dirección
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Asocia el socket a la dirección y puerto especificados
        server_sock.bind(addr)
        # Configura el socket para escuchar conexiones entrantes
        server_sock.listen(1)
        # Registra el manejador para aceptar nuevas conexiones
        server_sock.setsockopt(socket.SOL_SOCKET, 20,
                            lambda s: accept_client(s))
        print('Listening on', addr)


# Inicialización
wifi_manager = WiFiManager(SSID, PASSWORD)
mqtt_manager = MQTTManager(cliente_id, mqtt_broker, puerto)
espnow_manager = ESPNowManager(peer_mac, mensaje_clave)

mqtt_manager.set_callback(mensaje_callback)
mqtt_manager.subscribe(topic_prueba)

espnow_manager.set_mqtt_client(mqtt_manager) #permite el acceso al cliente mqtt desde espnow

# Iniciar servidor HTTP
alloc_emergency_exception_buf(100)
start_server()

while True:
    try:
        mqtt_manager.check_msg()  # Revisa si hay mensajes nuevos
        time.sleep(1)  # Espera un poco antes de la siguiente verificación
    except Exception as e:
        print(f"Error al recibir mensajes: {e}")