import network
import espnow
import time
from umqtt.simple import MQTTClient

SSID = "quepasapatejode"   # Nombre de la red WiFi 
PASSWORD = "losvilla08"    # Contraseña de la red WiFi
# Configuración del cliente MQTT
cliente_id = 'dispositivo1'
mqtt_broker = '192.168.1.11'
puerto = 1883

# Diccionario para mapear direcciones MAC a nombres
MAC_A_NOMBRE = {
    b'\x08\xb6\x1f\x81\x19 ': {
        "nombre": "sensor-DHT11", 
        "topics": ["sensor/dht11/temp", "sensor/dht11/hum"]
    },
    b'00\xf9\xed\xd0\xe4': {
        "nombre": "sensor-LM35", 
        "topics": ["sensor/lm35"]
    },
    # Agrega aquí otras direcciones MAC, sus nombres y topics
}

def wifi_reset():
    sta = network.WLAN(network.STA_IF); sta.active(False)
    ap = network.WLAN(network.AP_IF); ap.active(False)
    sta.active(True)    # Activar el modo estación
    while not sta.active():   
        time.sleep(0.1)
    sta.disconnect()   
    while sta.isconnected():   # Esperar hasta que se desconecte de cualquier red WiFi anterior
        time.sleep(0.1)
    return sta, ap   # Devolver los objetos de estación y punto de acceso

# Función de callback para recibir datos
def recv_cb(e):
    while True:    # Leer todos los mensajes que esperan en el búfer
        mac, msg = e.irecv(0)   # No esperar si no hay mensajes
        if mac is None:   # Si no hay dirección MAC, salir del bucle
            return
        data = MAC_A_NOMBRE.get(mac, {"nombre": "desconocido", "topic": "unknown/topic"})
        print("Mensaje recibido de:", data["nombre"])
        print("MAC:", mac)
        print("Mensaje:", msg)
        proccess_send_msg(data,msg)  # Procesar el mensaje recibido

def proccess_send_msg(data,msg):
    # Decodificar el mensaje de bytearray a string
    mensaje_decodificado = msg.decode('utf-8')
    print("Mensaje decodificado:", mensaje_decodificado)
    
    if data["nombre"] == "sensor-DHT11":
        try:
            temp, hum = mensaje_decodificado.split(';')
            cliente.publish(data["topics"][0], temp)
            cliente.publish(data["topics"][1], hum)
        except ValueError:
            print("Error al procesar el mensaje del sensor DHT11")
    else:
        cliente.publish(data["topics"][0], mensaje_decodificado)

def conectar_wifi(ssid,password):
    sta = network.WLAN(network.STA_IF)
    sta.connect(ssid, password)
    
    while not sta.isconnected():
        time.sleep(0.1)
    
    print("Conectado a:", ssid)
    print("Dirección IP:", sta.ifconfig()[0])
    
    sta.config(pm=sta.PM_NONE)   # Deshabilitar el ahorro de energía después de la conexión
    print("Proxy corriendo en el canal:", sta.config("channel")) # Imprimir el canal en el que se está ejecutando
    
    return sta

def activar_espNow():
    e = espnow.ESPNow()
    e.active(True)
    # Verificación de activación
    if e.active():
        print("Se activo ESP-NOW")
        return e
    else:
        # Manejar el caso en el que la activación falló
        raise RuntimeError("No se pudo activar ESP-NOW")

def conectar_mqtt(cliente_id, mqtt_broker, puerto):
    cliente = MQTTClient(cliente_id, mqtt_broker, port=puerto)
    while True:
        try:
            cliente.connect()
            print("Conectado al broker MQTT")
            break
        except Exception as e:
            print(f"Error al conectar al broker MQTT: {e}")
            time.sleep(5)  # Espera 5 segundos antes de reintentar
    return cliente

sta, ap = wifi_reset()

sta = conectar_wifi(SSID,PASSWORD)  

e = activar_espNow()

# Asignar la función de callback a ESP-NOW
e.irq(recv_cb)   # Establecer la función recv_cb como la función de callback para manejar los datos recibidos

cliente = conectar_mqtt(cliente_id, mqtt_broker, puerto)

#topic_ejemplo = b'test/espnow'

#cliente.publish(topic_ejemplo, "Hola desde ESP-NOW")