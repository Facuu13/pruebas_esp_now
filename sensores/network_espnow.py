import network
import espnow
import time
import json
import re

class SensorBase:
    def __init__(self):
        self.peer_mac = b'\xff' * 6
        self.sta, self.ap = self.wifi_reset()
        self.mac_propia = (self.sta.config('mac')).hex()
        self.e = self.setup_espnow(self.peer_mac)
        self.buscar_canal()
        self.e.irq(self.recv_cb)
        
    def wifi_reset(self):
        """
        Reinicia la configuración WiFi.
        """
        sta = network.WLAN(network.STA_IF)
        sta.active(False)
        ap = network.WLAN(network.AP_IF)
        ap.active(False)
        sta.active(True)
        while not sta.active():
            time.sleep(0.1)
        sta.disconnect()
        while sta.isconnected():
            time.sleep(0.1)
        return sta, ap

    def setup_espnow(self, peer_mac):
        """
        Configura ESP-NOW y añade el peer MAC.
        """
        e = espnow.ESPNow()
        e.active(True)
        e.add_peer(peer_mac)
        return e

    def buscar_canal(self):
        """
        Busca el canal correcto enviando mensajes de prueba en cada canal.
        """
        for canal in range(1, 14):  # Canales WiFi 1 a 13
            self.sta.config(channel=canal)
            mensaje = json.dumps({"palabra_clave": "buscar_canal"})
            self.e.send(self.peer_mac, mensaje)
            print(f"Enviando mensaje de prueba en el canal: {canal}")
            start_time = time.time()
            while time.time() - start_time < 1:  # Esperar 1 segundo por una respuesta
                mac, msg = self.e.irecv(0)
                if mac and msg:
                    try:
                        data = json.loads(msg)
                        if data.get("respuesta") == "canal_correcto":
                            print(f"Canal correcto encontrado: {canal}")
                            return
                    except Exception as ex:
                        print("Error procesando el mensaje de respuesta:", ex)
            time.sleep(0.1)

    def recv_cb(self,e):
        """
        Callback para recibir datos ESP-NOW.
        """
        while True:
            mac, msg = self.e.irecv(0)
            if mac is None:
                return
            self.procesar_mensaje(mac, msg)
    

    def send_sensor_data(self):
        """
        Método abstracto que debe ser implementado por las subclases.
        """
        raise NotImplementedError("Subclass must implement send_sensor_data()")
    
    def extraer_mac(self,topic):
        """
        Extrae el mac del topic que sigue a /sensor/
        """
        match = re.search(r'/sensor/([^/]+)(?:/|$)', topic)
        if match:
            return match.group(1)
        return None
    
    def procesar_mensaje(self, mac, msg):
        """
        Procesa el mensaje recibido, convirtiéndolo en un formato adecuado
        """
        try:
            data = json.loads(msg)
            topic = data.get("topic")
            value = data.get("value")
            if topic and value is not None:
                print("Topic_general:", topic)
                print("Value:", value)
                
                # Extraer la mac usando la función auxiliar
                identifier = self.extraer_mac(topic)
                if identifier:
                    print("Identificador extraído:", identifier)
                if identifier == self.mac_propia:
                    print("Son la misma MAC")
            else:
                print("No se pudo extraer el identificador del topic")
        
        except Exception as ex:
            print("Error procesando el mensaje:", ex)
