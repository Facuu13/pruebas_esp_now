# http_server.py

import socket
from micropython import alloc_emergency_exception_buf
import json
import machine

received_data = {}

espnow_manager = None  # Añadir esta variable global
peer_mac = b'\xff' * 6

def set_espnow_manager(manager):
    global espnow_manager
    espnow_manager = manager

def handle_update_relay(cl, request_lines):
    try:
        # Leer el cuerpo de la solicitud
        body = request_lines[-1]
        data = json.loads(body)
        mac = data['mac']
        topic = data['topic']
        state = data['state']
        
        # Extraer el número del relé desde el topic (último número del topic)
        relay_number = topic.split('/')[-1]  # Extraemos el número del relé del topic
        mac_sensor = mac.split("/")[0] # Extraemos la mac del sensor

        # Actualizar el estado en received_data
        new_topic = f"{mac}"
        received_data[new_topic] = {'topic': topic, 'value': state}

        # Si espnow_manager está disponible, enviamos los datos por ESP-NOW
        if espnow_manager:
            topic_final = f"/sensor/{mac_sensor}/rele/set/{relay_number}"
            mensaje ={
                "topic":topic_final,
                "value": state
            }
            espnow_manager.send_encrypted_data(mensaje)
            print(f"Enviado por ESP-NOW: {mensaje}")

        # Responder al cliente
        response = {'status': 'success'}
    except Exception as e:
        print('Error:', e)
        response = {'status': 'error', 'message': str(e)}
    
    response_body = json.dumps(response)
    cl.send(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n" + response_body.encode())

def handle_get_config():
    try:
        with open('config/config.json', 'r') as f:
            config = json.load(f)
        response_body = json.dumps(config)
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{response_body}".encode()
    except Exception as e:
        print(f"Error al leer config.json: {e}")
        return b"HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\nError interno del servidor"

def handle_update_config(cl, request_lines):
    try:
        # Leer el cuerpo de la solicitud
        body = request_lines[-1]
        data = json.loads(body)

        # Validación de campos y tipos
        campos_requeridos = {
            "mode": str,
            "ssid": str,
            "password": str,
            "ap_ssid": str,
            "ap_password": str,
            "cliente_id": str,
            "mqtt_broker": str,
            "mqtt_user": str,
            "mqtt_pass": str,
            "puerto": int,
            "year": (int, type(None)),  # Permitir NULL o int
            "month": (int, type(None)), # Permitir NULL o int
            "day": (int, type(None)),   # Permitir NULL o int
            "hour": (int, type(None)),  # Permitir NULL o int
            "minute": (int, type(None)) # Permitir NULL o int
        }

        # Comprobar que todos los campos requeridos están presentes y tienen el tipo correcto
        for campo, tipo in campos_requeridos.items():
            if campo not in data:
                raise ValueError(f"Falta el campo '{campo}'")
            if not isinstance(data[campo], tipo):
                raise TypeError(f"El campo '{campo}' debe ser de tipo {tipo[0].__name__} o {tipo[1].__name__}")
        
        # Validar el valor de 'mode'
        if data['mode'] not in ["CL", "AP"]:
            raise ValueError("El campo 'mode' solo puede ser 'CL' o 'AP'")
        
        # Leer la configuración actual
        with open('config/config.json', 'r') as f:
            config = json.load(f)

        # Actualizar los campos en la configuración
        for campo in campos_requeridos:
            config[campo] = data[campo]

        # Guardar la nueva configuración
        with open('config/config.json', 'w') as f:
            json.dump(config, f)
        
        # Responder al cliente
        response = {'status': 'success'}
        
        # Reiniciar el dispositivo para aplicar la nueva configuración
        machine.reset()

    except (ValueError, TypeError) as e:
        print(f"Error en los datos de configuración: {e}")
        response = {'status': 'error', 'message': str(e)}
    except Exception as e:
        print(f"Error general actualizando configuración: {e}")
        response = {'status': 'error', 'message': 'Error interno'}
    finally:
        # Responder al cliente en cualquier caso
        response_body = json.dumps(response)
        cl.send(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n" + response_body.encode())


def handle_login():
    try:
        with open('frontend/login.html', 'r') as f:
            content = f.read()
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{content}".encode()
    except Exception as e:
        print(f"Error al leer index.html: {e}")
        return b"HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\nError interno del servidor"

def handle_root():
    try:
        with open('frontend/index.html', 'r') as f:
            content = f.read()
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{content}".encode()
    except Exception as e:
        print(f"Error al leer index.html: {e}")
        return b"HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\nError interno del servidor"

def handle_config():
    try:
        with open('frontend/config.html', 'r') as f:
            content = f.read()
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{content}".encode()
    except Exception as e:
        print(f"Error al leer config.html: {e}")
        return b"HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\nError interno del servidor"

def handle_status():
    return b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nStatus: OK"

def handle_not_found():
    return b"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nNot Found"

def handle_data():
    global received_data
    response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n"
    
    for mac, data in received_data.items():
        response += f"{mac}\n"
        response += f"{data['topic']}\n"
        response += f"{data['value']}\n"
        response += f"{data['modelo']}\n"
        response += f"{data['hora']}\n"
        response += "\n"

    return response.encode()

def handle_static_file(path):
    try:
        with open(path, 'rb') as f:  # Abrimos en modo binario
            content = f.read()

        # Determinamos el tipo de contenido según la extensión del archivo
        if path.endswith('.css'):
            content_type = 'text/css'
        elif path.endswith('.js'):
            content_type = 'application/javascript'
        elif path.endswith('.html'):
            content_type = 'text/html'
        elif path.endswith('.png'):
            content_type = 'image/png'
        elif path.endswith('.jpg') or path.endswith('.jpeg'):
            content_type = 'image/jpeg'
        else:
            content_type = 'application/octet-stream'  # Tipo por defecto para otros archivos

        return f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n".encode() + content
    except Exception as e:
        print(f"Error al leer {path}: {e}")
        return b"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nNot Found"


def handle_client(cl):
    try:
        request = cl.recv(1024)  # Recibe la petición del cliente
        request_lines = request.split(b'\r\n')
        request_line = request_lines[0]
        method, path, _ = request_line.split(b' ')

        if method == b'GET':
            if path == b'/':
                response = handle_login()
            elif path == b'/home':  # Ruta para la página de home
                response = handle_root() 
            elif path == b'/config':  # Ruta para la página de configuración
                response = handle_config()
            elif path == b'/get_config':  # Ruta para obtener la configuración actual
                response = handle_get_config()
            elif path == b'/status':
                response = handle_status()
            elif path == b'/data':
                response = handle_data()
            else:
                response = handle_static_file(path[1:].decode())
        elif method == b'POST':
            if path == b'/update_relay':
                handle_update_relay(cl, request_lines)
                return
            elif path == b'/update_config':
                handle_update_config(cl, request_lines)
                return
            else:
                response = b"HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/plain\r\n\r\nMethod Not Allowed"
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
        cl.setsockopt(socket.SOL_SOCKET, 20, lambda x: handle_client(x))
    except Exception as e:
        print(f"Exception accepting client: {e}")

def start_server():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    server_sock = socket.socket()
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(addr)
    server_sock.listen(1)
    server_sock.setsockopt(socket.SOL_SOCKET, 20, lambda s: accept_client(s))
    print('Listening on', addr)
    alloc_emergency_exception_buf(100)
