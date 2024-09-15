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
        ESPNowConfig.buscar_canal(self.e, self.sta, self.peer_mac)
        self.e.irq(self.recv_cb)
        self.key = b"1234567890123456"  # Clave AES de 16 bytes para todos los sensores
        self.iv = b"ivfixed123456789"  # Debe tener exactamente 16 bytes
    
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

    def recv_cb(self, e):
        """
        Callback para recibir datos ESP-NOW.
        """
        while True:
            mac, msg = self.e.irecv(0)
            if mac is None:
                return

            # Diccionario de acciones
            acciones = {
                "rele/set": self.controlar_rele,
            }

            MessageProcessor.procesar_mensaje(self.mac_propia, mac, msg, acciones)


    def send_sensor_data_encriptado(self):
        """
        Método abstracto que debe ser implementado por las subclases.
        """
        raise NotImplementedError("Subclass must implement send_sensor_data_encriptado()")
    
    def send_rele_state_encriptado(self):
        """
        Método abstracto que debe ser implementado por las subclases.
        """
        raise NotImplementedError("Subclass must implement send_rele_state_encriptado()")

    def controlar_rele(self, estado):
        """
        Método abstracto para controlar el relé que debe ser implementado por las subclases.
        """
        raise NotImplementedError("Subclass must implement controlar_rele()")
