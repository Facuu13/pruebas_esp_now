import time
import machine
from network_espnow import SensorBase
import json

class SensorPrueba(SensorBase):
    def __init__(self):
        super().__init__()

    def procesar_mensaje(self, mac, msg):
        """
        Procesa el mensaje recibido, convirtiéndolo en un formato adecuado
        """
        try:
            data = json.loads(msg)
            topic = data.get("topic")
            value = data.get("value")
            if topic and value is not None:
                print("Topic_general:", topic)
                print("Value:", value)
        except Exception as ex:
            print("Error procesando el mensaje:", ex)
    
    def send_sensor_data(self):
        for i in range(100):
            data = {
                    "topic": "sensor/prueba",
                    "value": i
                }
            data_str = json.dumps(data)
            self.e.send(self.peer_mac, data_str)
            print("Mensaje enviado:", data_str)
            time.sleep(1)
            
# from sensor_prueba import SensorPrueba
# sensor = SensorPrueba()
# sensor.send_sensor_data()