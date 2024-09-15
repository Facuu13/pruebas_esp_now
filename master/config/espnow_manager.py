import network
import espnow
import time
import json
from http_server import received_data

class ESPNowManager:
    def __init__(self, peer_mac, mensaje_clave, modo_operacion="CL"):
        self.peer_mac = peer_mac
        self.mensaje_clave = mensaje_clave
        self.modo_operacion = modo_operacion  # Almacena el modo de operación
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