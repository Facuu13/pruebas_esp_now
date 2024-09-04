import time
from umqtt.simple import MQTTClient

class MQTTManager:
    def __init__(self, client_id, mqtt_broker, puerto, mqtt_user, mqtt_pass):
        self.cliente_id = client_id
        self.mqtt_broker = mqtt_broker
        self.puerto = puerto
        self.mqtt_user = mqtt_user
        self.mqtt_pass = mqtt_pass
        self.cliente = self.conectar_mqtt()
    
    def conectar_mqtt(self):
        cliente = MQTTClient(self.cliente_id, self.mqtt_broker, port=self.puerto, user=self.mqtt_user, password=self.mqtt_pass)
        max_intentos = 5
        intentos = 0
        while intentos < max_intentos:
            try:
                cliente.connect()
                print("Conectado al broker MQTT")
                return cliente
            except Exception as e:
                intentos += 1
                print(f"Error al conectar al broker MQTT: {e}")
                print(f"Intento {intentos}/{max_intentos}")
                time.sleep(5)
        raise RuntimeError(f"No se pudo conectar al broker MQTT después de {max_intentos} intentos")

    def set_callback(self, callback):
        self.cliente.set_callback(callback)

    def subscribe(self, topic):
        try:
            self.cliente.subscribe(topic)
            print("Suscripción exitosa al topic:", topic)
        except Exception as e:
            print(f"Error al suscribirse al topic: {e}")

    def publish(self, topic, mensaje):
        self.cliente.publish(topic, mensaje)

    def check_msg(self):
        self.cliente.check_msg()