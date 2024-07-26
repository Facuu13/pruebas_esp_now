import network
import espnow
import time

class SensorBase:
    def __init__(self):
        self.peer_mac = b'\xff' * 6
        self.sta, self.ap = self.wifi_reset()
        self.sta.config(channel=10)
        self.e = self.setup_espnow(self.peer_mac)

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

    def setup_espnow(self, peer_mac):
        e = espnow.ESPNow()
        e.active(True)
        e.add_peer(peer_mac)
        return e

    def send_sensor_data(self):
        raise NotImplementedError("Subclass must implement send_sensor_data()")
