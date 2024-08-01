import network
import espnow
import time
import json
from umqtt.simple import MQTTClient

SSID = "quepasapatejode"
PASSWORD = "losvilla08"
cliente_id = 'dispositivo1'
mqtt_broker = '192.168.1.11'
puerto = 1883
peer_mac = b'\xff' * 6
mensaje_clave = json.dumps({"respuesta": "canal_correcto"})

def wifi_reset():
    """
    Resetea las conexiones WiFi y activa el modo estación.
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

def procesar_mensaje(mac, msg):
    """
    Procesa el mensaje recibido, convirtiéndolo en un formato adecuado y publicándolo en MQTT.
    """
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
            cliente.publish(new_topic, str(value))
        elif info == "buscar_canal":
            e.send(peer_mac, mensaje_clave)
    except Exception as ex:
        print("Error procesando el mensaje:", ex)

def recv_cb(e):
    """
    Callback para recibir datos ESP-NOW.
    """
    while True:
        mac, msg = e.irecv(0)
        if mac is None:
            return
        procesar_mensaje(mac, msg)

def conectar_wifi(ssid, password):
    """
    Conecta a la red WiFi especificada.
    """
    sta = network.WLAN(network.STA_IF)
    sta.connect(ssid, password)
    while not sta.isconnected():
        time.sleep(0.1)
    print("Conectado a:", ssid)
    print("Dirección IP:", sta.ifconfig()[0])
    sta.config(pm=sta.PM_NONE)
    print("Proxy corriendo en el canal:", sta.config("channel"))
    return sta

def activar_espNow():
    """
    Activa ESP-NOW.
    """
    e = espnow.ESPNow()
    e.active(True)
    e.add_peer(peer_mac)
    if e.active():
        print("Se activo ESP-NOW")
        return e
    else:
        raise RuntimeError("No se pudo activar ESP-NOW")

def conectar_mqtt(cliente_id, mqtt_broker, puerto):
    """
    Conecta al broker
    """
    cliente = MQTTClient(cliente_id, mqtt_broker, port=puerto)
    max_intentos=5
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

# Inicialización
sta, ap = wifi_reset()
sta = conectar_wifi(SSID, PASSWORD)
cliente = conectar_mqtt(cliente_id, mqtt_broker, puerto)
e = activar_espNow()
e.irq(recv_cb)

