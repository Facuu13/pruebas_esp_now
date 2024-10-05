import network
import espnow
import json
import cryptolib
import ubinascii
from http_server import received_data

# Definición de constantes para la clave y el IV
AES_KEY = b"1234567890123456"
AES_IV = b"ivfixed987654321"  # IV de 16 bytes


class ESPNowError(Exception):
    """Excepción personalizada para manejar errores en ESP-NOW."""
    pass


class ESPNowManager:
    def __init__(self, peer_mac, mensaje_clave, modo_operacion, hora):
        self.peer_mac = peer_mac
        self.mensaje_clave = mensaje_clave
        self.modo_operacion = modo_operacion
        self.hora = hora
        self.e = self.activar_esp_now()
        self.e.irq(self.recv_cb)
        self.topic_discovery = "/discovery"

    def activar_esp_now(self):
        """Activa ESP-NOW y agrega un par."""
        e = espnow.ESPNow()
        e.active(True)
        e.add_peer(self.peer_mac)
        if not e.active():
            raise ESPNowError("No se pudo activar ESP-NOW")
        print("Se activó ESP-NOW")
        return e

    def cifrar_datos(self, data_str):
        """Cifra los datos usando AES en modo CBC."""
        data_str_padded = self.pad_data(data_str)
        aes = cryptolib.aes(AES_KEY, 2, AES_IV)
        encrypted_data = aes.encrypt(data_str_padded)
        return AES_IV, encrypted_data

    def pad_data(self, data_str):
        """Aplica padding a los datos para que sean múltiplos de 16."""
        pad_length = 16 - (len(data_str) % 16)
        return data_str + ' ' * pad_length

    def send_encrypted_data(self, data):
        """Cifra y envía los datos por ESP-NOW."""
        payload = self.build_payload(data)
        self.e.send(self.peer_mac, payload)

    def build_payload(self, data):
        """Construye el payload a partir de datos cifrados."""
        data_str = json.dumps(data)
        iv, encrypted_data = self.cifrar_datos(data_str)
        return json.dumps({
            "iv": ubinascii.hexlify(iv).decode('utf-8'),
            "data": ubinascii.hexlify(encrypted_data).decode('utf-8')
        })

    def send(self, mensaje):
        """Envía un mensaje sin cifrado."""
        self.e.send(self.peer_mac, mensaje)

    def desencriptar_datos(self, iv_hex, encrypted_data_hex):
        """Desencripta los datos usando AES en modo CBC."""
        iv = ubinascii.unhexlify(iv_hex)
        encrypted_data = ubinascii.unhexlify(encrypted_data_hex)
        aes = cryptolib.aes(AES_KEY, 2, iv)
        decrypted_data = aes.decrypt(encrypted_data)
        return self.unpad_data(decrypted_data)

    def unpad_data(self, data):
        """Elimina el padding de los datos desencriptados."""
        return data.rstrip().decode('utf-8')

    def recv_cb(self, e):
        """Callback para recibir mensajes por ESP-NOW."""
        while True:
            mac, msg = e.irecv(0)
            if mac is None:
                return
            self.process_received_message(mac, msg)

    def process_received_message(self, mac, msg):
        """Procesa el mensaje recibido y ejecuta acciones correspondientes."""
        try:
            data = json.loads(msg)
            iv_hex = data.get("iv")
            encrypted_data_hex = data.get("data")

            if iv_hex and encrypted_data_hex:
                decrypted_data = self.desencriptar_datos(iv_hex, encrypted_data_hex)
                print("Datos desencriptados:", decrypted_data)
                self.procesar_mensaje(mac, decrypted_data)

        except Exception as ex:
            print("Error procesando el mensaje encriptado:", ex)

    def procesar_mensaje(self, mac, msg):
        """Procesa el mensaje y actualiza el estado del sistema."""
        try:
            data = json.loads(msg)
            info = data.get("palabra_clave")
            topic = data.get("topic")
            value = data.get("value")
            modelo = data.get("modelo")
            hora_actual = self.hora.devolver_hora_actual()

            if topic and value is not None:
                self.update_received_data(mac, topic, value, modelo, hora_actual)
                if self.modo_operacion == "CL":
                    self.publish_to_mqtt(mac, topic, value)

            elif info == "buscar_canal":
                self.send(self.mensaje_clave)
                print(f"Nuevo nodo detectado: {mac.hex()}")

            elif info == "verificar_canal":
                self.send(json.dumps({"respuesta": "verificacion_exitosa"}))
                print("Nodo Aceptado")
                if self.modo_operacion == "CL":
                    self.publish_discovery(mac)

        except Exception as ex:
            print("Error procesando el mensaje:", ex)

    def update_received_data(self, mac, topic, value, modelo, hora_actual):
        """Actualiza los datos recibidos en la estructura global."""
        new_mac = mac.hex()
        new_topic = f"{new_mac}/{topic}"
        print(f"Topic general: {new_topic}, Value: {value}")
        received_data[new_topic] = {
            "topic": topic,
            "value": value,
            "modelo": modelo,
            "hora": hora_actual
        }

    def publish_to_mqtt(self, mac, topic, value):
        """Publica los datos en MQTT."""
        new_topic = f"{mac.hex()}/{topic}"
        self.mqtt_client.publish(new_topic, str(value))

    def publish_discovery(self, mac):
        """Publica la información del nodo en el tópico de descubrimiento."""
        self.mqtt_client.publish(self.topic_discovery, str(mac.hex()))

    def set_mqtt_client(self, mqtt_client):
        """Establece el cliente MQTT para la publicación."""
        self.mqtt_client = mqtt_client
