import espnow
import time
import json

class ESPNowConfig:
    @staticmethod
    def setup_espnow(peer_mac):
        """
        Configura ESP-NOW y añade el peer MAC.
        """
        e = espnow.ESPNow()
        e.active(True)
        e.add_peer(peer_mac)
        return e

    @staticmethod
    def buscar_canal(e, sta, peer_mac):
        """
        Busca el canal correcto enviando mensajes de prueba en cada canal.
        """
        for canal in range(1, 14):  # Canales WiFi 1 a 13
            sta.config(channel=canal)
            mensaje = json.dumps({"palabra_clave": "buscar_canal"})
            e.send(peer_mac, mensaje)
            print(f"Enviando mensaje de prueba en el canal: {canal}")
            start_time = time.time()
            while time.time() - start_time < 1:  # Esperar 1 segundo por una respuesta
                mac, msg = e.irecv(0)
                if mac and msg:
                    try:
                        data = json.loads(msg)
                        if data.get("respuesta") == "canal_correcto":
                            print(f"Canal correcto encontrado: {canal}")
                            return
                    except Exception as ex:
                        print("Error procesando el mensaje de respuesta:", ex)
            time.sleep(0.1)
