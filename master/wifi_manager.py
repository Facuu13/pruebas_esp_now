import network
import time

class WiFiManager:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.sta, self.ap = self.wifi_reset()
        self.conectar_wifi()
    
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
    
    def conectar_wifi(self):
        self.sta.connect(self.ssid, self.password)
        while not self.sta.isconnected():
            time.sleep(0.1)
        print("Conectado a:", self.ssid)
        print("Dirección IP:", self.sta.ifconfig()[0])
        self.sta.config(pm=self.sta.PM_NONE)
        print("Proxy corriendo en el canal:", self.sta.config("channel"))