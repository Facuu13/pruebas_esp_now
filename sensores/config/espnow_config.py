import espnow
import time
import json
import ubinascii
import cryptolib
import machine

class ESPNowConfig:
    @staticmethod
    def setup_espnow(peer_mac):
        """
        Configura ESP-NOW y añade el peer MAC.
        """
        try:
            e = espnow.ESPNow()
            e.active(True)
            e.add_peer(peer_mac)
            print("ESP-NOW configurado correctamente.")
            return e
        except Exception as ex:
            print(f"Error configurando ESP-NOW: {ex}")
            machine.reset()

    @staticmethod
    def _aplicar_padding(mensaje):
        """
        Añade padding a los mensajes para cumplir con la longitud requerida por AES.
        """
        pad = 16 - (len(mensaje) % 16)
        return mensaje + ' ' * pad

    @staticmethod
    def cifrar_mensaje(mensaje, key, iv):
        """
        Cifra un mensaje usando AES en modo CBC.
        """
        try:
            mensaje_padded = ESPNowConfig._aplicar_padding(mensaje)
            aes = cryptolib.aes(key, 2, iv)  # Crear instancia AES en modo CBC
            encrypted_message = aes.encrypt(mensaje_padded)  # Cifrar datos
            iv_hex = ubinascii.hexlify(iv).decode('utf-8')
            encrypted_message_hex = ubinascii.hexlify(encrypted_message).decode('utf-8')

            return json.dumps({"iv": iv_hex, "data": encrypted_message_hex})
        except Exception as ex:
            print(f"Error cifrando mensaje: {ex}")
            return None

    @staticmethod
    def desencriptar_mensaje(iv_hex, encrypted_data_hex, key):
        """
        Desencripta los datos usando AES en modo CBC.
        """
        try:
            iv = ubinascii.unhexlify(iv_hex)  # Convertir IV de hex a bytes
            encrypted_data = ubinascii.unhexlify(encrypted_data_hex)  # Convertir datos cifrados de hex a bytes
            aes = cryptolib.aes(key, 2, iv)  # Crear instancia AES en modo CBC con el IV recibido
            decrypted_data_padded = aes.decrypt(encrypted_data)  # Desencriptar datos
            decrypted_data = decrypted_data_padded.rstrip()  # Eliminar padding

            return decrypted_data.decode('utf-8')
        except Exception as ex:
            print(f"Error desencriptando mensaje: {ex}")
            return None

    @staticmethod
    def recibir_mensaje(e, timeout):
        """
        Recibe un mensaje de ESP-NOW dentro de un tiempo de espera determinado.
        Devuelve el MAC y el mensaje procesado o None si no hay respuesta.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            mac, msg = e.irecv(0)
            if mac and msg:
                try:
                    return mac, json.loads(msg)
                except json.JSONDecodeError:
                    print("Error decodificando el mensaje JSON.")
                    return None
                except Exception as ex:
                    print(f"Error procesando el mensaje: {ex}")
                    return None
        return None, None  # Si no se recibe nada

    @staticmethod
    def buscar_canal(e, sta, peer_mac, key, iv):
        """
        Busca el canal correcto enviando mensajes de prueba en cada canal.
        """
        for canal in range(1, 14):  # Canales WiFi 1 a 13
            try:
                sta.config(channel=canal)
                mensaje = json.dumps({"palabra_clave": "buscar_canal"})
                mensaje_cifrado = ESPNowConfig.cifrar_mensaje(mensaje, key, iv)

                if mensaje_cifrado:
                    e.send(peer_mac, mensaje_cifrado)
                    print(f"Enviando mensaje de prueba en el canal: {canal}")
                else:
                    print(f"Error cifrando mensaje para el canal {canal}.")
                    continue

                mac, data = ESPNowConfig.recibir_mensaje(e, 1)  # Esperar 1 segundo
                if data and data.get("respuesta") == "canal_correcto":
                    print(f"Canal correcto encontrado: {canal}")
                    if ESPNowConfig.verificar_canal(e, peer_mac, key, iv):
                        print("Canal verificado correctamente.")
                        return
                    else:
                        print("Verificación fallida, reiniciando...")
                        machine.reset()
            except Exception as ex:
                print(f"Error al intentar en el canal {canal}: {ex}")
                continue

        print("No se encontró el canal correcto. Reiniciando...")
        machine.reset()

    @staticmethod
    def verificar_canal(e, peer_mac, key, iv):
        """
        Envía un mensaje de verificación al nodo central para confirmar que el canal es correcto.
        Si no hay respuesta en un tiempo determinado, retorna False.
        """
        try:
            mensaje = json.dumps({"palabra_clave": "verificar_canal"})
            mensaje_cifrado = ESPNowConfig.cifrar_mensaje(mensaje, key, iv)
            if mensaje_cifrado:
                e.send(peer_mac, mensaje_cifrado)
                print("Enviando mensaje de verificación...")

                mac, data = ESPNowConfig.recibir_mensaje(e, 2)  # Esperar 2 segundos
                if data and data.get("respuesta") == "verificacion_exitosa":
                    return True  # Verificación exitosa
            else:
                print("Error cifrando el mensaje de verificación.")
        except Exception as ex:
            print(f"Error en verificar_canal: {ex}")
        return False  # No hubo respuesta o fue incorrecta
