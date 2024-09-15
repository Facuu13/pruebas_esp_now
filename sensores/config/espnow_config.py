import espnow
import time
import json

import ubinascii
import cryptolib

class ESPNowConfig:
    @staticmethod
    def setup_espnow(peer_mac):
        """
        Configura ESP-NOW y añade el peer MAC.
        """
        e = espnow.ESPNow()
        e.active(True)
        e.add_peer(peer_mac)
        return e
    
    def cifrar_mensaje(mensaje, key, iv):
        """
        Cifra un mensaje usando AES en modo CBC.
        """
        pad = 16 - (len(mensaje) % 16)
        mensaje_padded = mensaje + ' ' * pad  # Añadir padding

        aes = cryptolib.aes(key, 2, iv)  # Crear instancia AES en modo CBC
        encrypted_message = aes.encrypt(mensaje_padded)  # Cifrar datos
        iv_hex = ubinascii.hexlify(iv).decode('utf-8')
        encrypted_message_hex = ubinascii.hexlify(encrypted_message).decode('utf-8')

        return json.dumps({"iv": iv_hex, "data": encrypted_message_hex})

    @staticmethod
    def buscar_canal(e, sta, peer_mac, key, iv):
        """
        Busca el canal correcto enviando mensajes de prueba en cada canal.
        """
        for canal in range(1, 14):  # Canales WiFi 1 a 13
            sta.config(channel=canal)
            mensaje = json.dumps({"palabra_clave": "buscar_canal"})
            mensaje_cifrado = ESPNowConfig.cifrar_mensaje(mensaje, key, iv)
            e.send(peer_mac, mensaje_cifrado)
            print(f"Enviando mensaje de prueba en el canal: {canal}")
            start_time = time.time()
            while time.time() - start_time < 1:  # Esperar 1 segundo por una respuesta
                mac, msg = e.irecv(0)
                if mac and msg:
                    try:
                        data = json.loads(msg)
                        if data.get("respuesta") == "canal_correcto":
                            print(f"Canal correcto encontrado: {canal}")
                            return
                    except Exception as ex:
                        print("Error procesando el mensaje de respuesta:", ex)
            time.sleep(0.1)
