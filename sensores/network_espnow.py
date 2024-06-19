import network
import espnow
import time

def wifi_reset():
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

def setup_espnow(peer_mac):
    e = espnow.ESPNow()
    e.active(True)
    e.add_peer(peer_mac)
    return e