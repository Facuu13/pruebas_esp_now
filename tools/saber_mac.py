import network

# Obtener la dirección MAC
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
mac = wlan.config('mac')

# Imprimir la dirección MAC en formato legible
print(':'.join('%02x' % b for b in mac))
