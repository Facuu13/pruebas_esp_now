import network
import espnow
import time
import json
from http_server import received_data

import cryptolib
import ubinascii


class ESPNowManager:
    def __init__(self, peer_mac, mensaje_clave, modo_operacion="CL"):
        self.peer_mac = peer_mac
        self.mensaje_clave = mensaje_clave
        self.modo_operacion = modo_operacion  # Almacena el modo de operación
        self.e = self.activar_espNow()
        self.e.irq(self.recv_cb)
        self.topic_discovery = "/discovery"
        self.key = b"1234567890123456"
        self.iv = b"ivfixed987654321"  # Debe tener exactamente 16 bytes
    
    def activar_espNow(self):
        e = espnow.ESPNow()
        e.active(True)
        e.add_peer(self.peer_mac)
        if e.active():
            print("Se activó ESP-NOW")
            return e
        else:
            raise RuntimeError("No se pudo activar ESP-NOW")
    
    def cifrar_datos(self, data_str):
        """
        Cifra los datos usando AES en modo CBC.
        """
        pad = 16 - (len(data_str) % 16)
        data_str_padded = data_str + ' ' * pad  # Añadir padding

        aes = cryptolib.aes(self.key, 2, self.iv)  # Crear instancia AES en modo CBC
        
        encrypted_data = aes.encrypt(data_str_padded)  # Cifrar datos
        return self.iv, encrypted_data  # Devolver IV y datos cifrados
    
    def send_encrypted_data(self, data):
        """
        Cifra y envía los datos por ESP-NOW.
        """
        data_str = json.dumps(data)  # Convertir los datos a cadena JSON
        
        # Cifrar los datos
        iv, encrypted_data = self.cifrar_datos(data_str)
        
        # Convertir IV y datos cifrados a hexadecimal para enviar
        iv_hex = ubinascii.hexlify(iv)
        encrypted_data_hex = ubinascii.hexlify(encrypted_data)

        # Construir el payload
        payload = {
            "iv": iv_hex.decode('utf-8'),
            "data": encrypted_data_hex.decode('utf-8')
        }

        payload_str = json.dumps(payload)
        self.e.send(self.peer_mac, payload_str)  # Enviar mensaje cifrado
        print("Mensaje encriptado enviado:", payload_str)

    def send(self, mensaje):
        self.e.send(self.peer_mac, mensaje)

    def desencriptar_datos(self, iv_hex, encrypted_data_hex):
        """
        Desencripta los datos usando AES en modo CBC.
        """
        iv = ubinascii.unhexlify(iv_hex)  # Convertir IV de hex a bytes
        encrypted_data = ubinascii.unhexlify(encrypted_data_hex)  # Convertir datos cifrados de hex a bytes

        aes = cryptolib.aes(self.key, 2, iv)  # Crear instancia AES en modo CBC con el IV recibido
        decrypted_data_padded = aes.decrypt(encrypted_data)  # Desencriptar datos
        decrypted_data = decrypted_data_padded.rstrip()  # Eliminar padding
        return decrypted_data.decode('utf-8')
    
    def recv_cb(self, e):
        while True:
            mac, msg = e.irecv(0)
            if mac is None:
                return
            
            try:
                data = json.loads(msg)
                iv_hex = data.get("iv")
                encrypted_data_hex = data.get("data")

                if iv_hex and encrypted_data_hex:
                    # Desencriptar los datos
                    decrypted_data = self.desencriptar_datos(iv_hex, encrypted_data_hex)
                    print("Datos desencriptados:", decrypted_data)
                    self.procesar_mensaje(mac, decrypted_data)

            except Exception as ex:
                print("Error procesando el mensaje encriptado:", ex)

    
    def procesar_mensaje(self, mac, msg):
        try:
            data = json.loads(msg)
            info = data.get("palabra_clave")
            topic = data.get("topic")
            value = data.get("value")
            if topic and value is not None:
                new_mac = mac.hex()
                new_topic = f"{new_mac}/{topic}"
                print("Topic_general:", new_topic)
                print("Value:", value)
                received_data[new_topic] = {
                    "topic": topic,
                    "value": value,
                    }
                # Solo publicar en MQTT si estamos en modo CL
                if self.modo_operacion == "CL":
                    self.mqtt_client.publish(new_topic, str(value))

            elif info == "buscar_canal":
                self.send(self.peer_mac, self.mensaje_clave)
                print("Nuevo nodo detectado")
                print("Nodo: ",mac.hex())
                # Solo publicar en MQTT si estamos en modo CL
                if self.modo_operacion == "CL":
                    self.mqtt_client.publish(self.topic_discovery, str(mac.hex()))
                    
        except Exception as ex:
            print("Error procesando el mensaje:", ex)
    
    def set_mqtt_client(self, mqtt_client):
        self.mqtt_client = mqtt_client