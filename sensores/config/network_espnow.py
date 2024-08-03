from wifi_config import WiFiConfig
from espnow_config import ESPNowConfig
from message_processor import MessageProcessor

class SensorBase:
    def __init__(self):
        self.peer_mac = b'\xff' * 6
        self.sta, self.ap = WiFiConfig.wifi_reset()
        self.mac_propia = (self.sta.config('mac')).hex()  # obtenemos la mac del chip
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
            MessageProcessor.procesar_mensaje(self.mac_propia, mac, msg, self.controlar_rele)

    def send_sensor_data(self):
        """
        Método abstracto que debe ser implementado por las subclases.
        """
        raise NotImplementedError("Subclass must implement send_sensor_data()")

    def controlar_rele(self, estado):
        """
        Método abstracto para controlar el relé que debe ser implementado por las subclases.
        """
        raise NotImplementedError("Subclass must implement controlar_rele()")
