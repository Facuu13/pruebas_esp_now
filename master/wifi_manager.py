import network
import time
import json

class WiFiManager:
    def __init__(self, config_path='config.json'):
        self.config = self.cargar_configuracion(config_path)
        self.sta, self.ap = self.wifi_reset()
        self.iniciar_wifi()
    
    def cargar_configuracion(self, config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def wifi_reset(self):
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
    
    def iniciar_wifi(self):
        modo = self.config.get("mode", "CL")
        if modo == "CL":
            self.conectar_wifi()
        elif modo == "AP":
            self.iniciar_modo_ap()
        else:
            print("Modo no reconocido. Iniciando en modo cliente por defecto.")
            self.conectar_wifi()

    def conectar_wifi(self):
        ssid = self.config.get("ssid")
        password = self.config.get("password")
        self.sta.connect(ssid, password)
        while not self.sta.isconnected():
            time.sleep(0.1)
        print("Conectado a:", ssid)
        print("Dirección IP:", self.sta.ifconfig()[0])
        self.sta.config(pm=self.sta.PM_NONE)
        print("Proxy corriendo en el canal:", self.sta.config("channel"))

    def iniciar_modo_ap(self):
        ap_ssid = self.config.get("ap_ssid", "ESP32_AP")
        ap_password = self.config.get("ap_password", "12345678")
        self.ap.active(True)
        self.ap.config(essid=ap_ssid, password=ap_password)
        print("Punto de acceso iniciado")
        print("SSID:", ap_ssid)
        print("Contraseña:", ap_password)
