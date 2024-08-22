from .wifi_config import WiFiConfig
from .espnow_config import ESPNowConfig
from .message_processor import MessageProcessor

class SensorBase:
    def __init__(self):
        self.peer_mac = b'\xff' * 6
        self.sta, self.ap = WiFiConfig.wifi_reset()
        self.mac_propia = (self.sta.config('mac')).hex()  # obtenemos la mac del chip
        self.enable_sensor = True
        self.e = ESPNowConfig.setup_espnow(self.peer_mac)
        ESPNowConfig.buscar_canal(self.e, self.sta, self.peer_mac)
        self.e.irq(self.recv_cb)

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
                "enable/set": self.habilitar_sensor,
            }

            MessageProcessor.procesar_mensaje(self.mac_propia, mac, msg, acciones)

    def habilitar_sensor(self, estado):
        """
        Habilita o deshabilita el sensor basado en el estado proporcionado.
        """
        if estado == "true":
            print("Habilitando sensor")
            self.enable_sensor = True
        elif estado == "false":
            print("Deshabilitando sensor")
            self.enable_sensor = False
        else:
            print("Valor incorrecto para habilitar/deshabilitar el sensor")

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
