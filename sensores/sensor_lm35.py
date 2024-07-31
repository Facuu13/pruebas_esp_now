import time
from machine import ADC, Pin
import json
from network_espnow import SensorBase

class SensorLM35(SensorBase):
    def __init__(self):
        super().__init__()
        # Configurar el pin GPIO34 como entrada analógica
        #self.adc = ADC(Pin(34)) #ESP32
        self.adc = ADC(Pin(0)) #ESP32C3M1
        self.adc.atten(ADC.ATTN_11DB)  # Configurar el rango de atenuación (0-3.3V)
        self.adc.width(ADC.WIDTH_12BIT)  # Configurar la resolución (12 bits: 0-4095)

    def read_temperature(self):
        # Leer el valor del ADC (0-4095)
        adc_value = self.adc.read()
        # Convertir el valor del ADC a voltaje (0-3.3V)
        voltage = adc_value / 4095.0 * 3.3
        # Convertir el voltaje a temperatura (Celsius)
        temperature = voltage * 100
        return round(temperature, 2)  # Redondeamos a 2 decimales
    
    def send_sensor_data(self):
        temp = self.read_temperature()
        if temp is not None:
            data = {
                    "topic": "sensor/temp",
                    "value": temp
                }
            data_str = json.dumps(data)
            self.e.send(self.peer_mac, data_str)
            print("Mensaje enviado:", data_str)
        else:
            print("Failed to read from sensor")
        time.sleep(2)

# from sensor_lm35 import SensorLM35

# sensor = SensorLM35()
# sensor.send_sensor_data()  # Solo llama a send_sensor_data una vez

#enviar dato en forma de struct topic y dato

#por ahora no filtrar

#gateway llevar lista de mac conocidas
#cuando llegue una mac desconocida preguntar si queremos agregarlo o no