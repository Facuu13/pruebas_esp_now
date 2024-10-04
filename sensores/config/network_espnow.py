from .wifi_config import WiFiConfig
from .espnow_config import ESPNowConfig
from .message_processor import MessageProcessor
import json

# Claves constantes
AES_KEY = b"1234567890123456"  # Clave AES de 16 bytes para todos los sensores
AES_IV = b"ivfixed123456789"    # Debe tener exactamente 16 bytes

class SensorBase:
    def __init__(self):
        self.peer_mac = b'\xff' * 6
        self.sta, self.ap = WiFiConfig.wifi_reset()
        self.mac_propia = (self.sta.config('mac')).hex()  # Obtenemos la MAC del chip
        self.e = ESPNowConfig.setup_espnow(self.peer_mac)  # Configuración de ESP-NOW
        ESPNowConfig.buscar_canal(self.e, self.sta, self.peer_mac, AES_KEY, AES_IV)
        self.e.irq(self.recv_cb)  # Configurar la interrupción para recibir mensajes
        
    def send_encrypted_data(self, data):
        """
        Cifra y envía los datos por ESP-NOW.
        """
        encrypted_payload = self.encrypt_and_prepare(data)
        self.e.send(self.peer_mac, encrypted_payload)
        print("Mensaje encriptado enviado:", encrypted_payload)

    def encrypt_and_prepare(self, data):
        """
        Convierte los datos a JSON y los cifra.
        """
        data_str = json.dumps(data)  # Convertir los datos a cadena JSON
        return ESPNowConfig.cifrar_mensaje(data_str, AES_KEY, AES_IV)

    def recv_cb(self, e):
        """
        Callback para recibir y desencriptar datos ESP-NOW.
        """
        while True:
            mac, msg = self.e.irecv(0)
            if mac is None:
                return
            self.process_received_message(mac, msg)

    def process_received_message(self, mac, msg):
        """
        Procesa el mensaje recibido y realiza la acción correspondiente.
        """
        try:
            data = json.loads(msg)
            iv_hex = data.get("iv")
            encrypted_data_hex = data.get("data")

            if iv_hex and encrypted_data_hex:
                decrypted_data = ESPNowConfig.desencriptar_mensaje(iv_hex, encrypted_data_hex, AES_KEY)
                print("Datos desencriptados:", decrypted_data)

                # Procesar el mensaje desencriptado
                acciones = {
                    "rele/set": self.controlar_rele,
                }
                MessageProcessor.procesar_mensaje(self.mac_propia, mac, decrypted_data, acciones)

        except Exception as ex:
            print("Error procesando el mensaje encriptado:", ex)

    def controlar_rele(self, rele_numero, estado):
        """
        Método abstracto para controlar el relé que debe ser implementado por las subclases.
        """
        raise NotImplementedError("Subclass must implement controlar_rele()")
