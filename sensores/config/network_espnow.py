from .wifi_config import WiFiConfig
from .espnow_config import ESPNowConfig
from .message_processor import MessageProcessor
import cryptolib
import ubinascii
import json

class SensorBase:
    def __init__(self):
        self.peer_mac = b'\xff' * 6
        self.sta, self.ap = WiFiConfig.wifi_reset()
        self.mac_propia = (self.sta.config('mac')).hex()  # obtenemos la mac del chip
        self.e = ESPNowConfig.setup_espnow(self.peer_mac)
        self.key = b"1234567890123456"  # Clave AES de 16 bytes para todos los sensores
        self.iv = b"ivfixed123456789"  # Debe tener exactamente 16 bytes
        ESPNowConfig.buscar_canal(self.e, self.sta, self.peer_mac, self.key, self.iv)
        self.e.irq(self.recv_cb)
        
    
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
        """
        Callback para recibir y desencriptar datos ESP-NOW.
        """
        while True:
            mac, msg = self.e.irecv(0)
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

                    # Procesar el mensaje desencriptado
                    acciones = {
                        "rele/set": self.controlar_rele,
                    }
                    MessageProcessor.procesar_mensaje(self.mac_propia, mac, decrypted_data, acciones)

            except Exception as ex:
                print("Error procesando el mensaje encriptado:", ex)

    def controlar_rele(self, estado):
        """
        Método abstracto para controlar el relé que debe ser implementado por las subclases.
        """
        raise NotImplementedError("Subclass must implement controlar_rele()")
