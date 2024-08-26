# http_server.py

import socket
from micropython import alloc_emergency_exception_buf

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
