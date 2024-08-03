import network
import time

class WiFiConfig:
    @staticmethod
    def wifi_reset():
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
