import network
import espnow
import time
import json

class ESPNowManager:
    def __init__(self, peer_mac, mensaje_clave):
        self.peer_mac = peer_mac
        self.mensaje_clave = mensaje_clave
        self.e = self.activar_espNow()
        self.e.irq(self.recv_cb)
        self.topic_discovery = "/discovery"
    
    def activar_espNow(self):
        e = espnow.ESPNow()
        e.active(True)
        e.add_peer(self.peer_mac)
        if e.active():
            print("Se activó ESP-NOW")
            return e
        else:
            raise RuntimeError("No se pudo activar ESP-NOW")

    def send(self, mac, mensaje):
        self.e.send(mac, mensaje)
    
    def recv_cb(self, e):
        while True:
            mac, msg = e.irecv(0)
            if mac is None:
                return
            self.procesar_mensaje(mac, msg)
    
    def procesar_mensaje(self, mac, msg):
        try:
            data = json.loads(msg)
            info = data.get("palabra_clave")
            topic = data.get("topic")
            value = data.get("value")
            word = data.get("word")
            if topic and value is not None and word == "encriptado":
                new_mac = mac.hex()
                new_topic = f"{new_mac}/{topic}"
                print("Topic_general:", new_topic)
                print("Value:", value)
                self.mqtt_client.publish(new_topic, str(value))
            elif info == "buscar_canal":
                self.send(self.peer_mac, self.mensaje_clave)
                print("Nuevo nodo detectado")
                print("Nodo: ",mac.hex())
                self.mqtt_client.publish(self.topic_discovery, str(mac.hex()))
        except Exception as ex:
            print("Error procesando el mensaje:", ex)
    
    def set_mqtt_client(self, mqtt_client):
        self.mqtt_client = mqtt_client