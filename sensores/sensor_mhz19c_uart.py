import time
from machine import UART, Pin
import json
from network_espnow import SensorBase

class SensorMHZ19UART(SensorBase):
    def __init__(self):
        super().__init__()
        self.buf=b'\xFF\x01\x86\x00\x00\x00\x00\x00\x79'
        # Configura los pines y la UART
        self.uart = UART(2, baudrate=9600, tx=17, rx=16)
    
    def read_mhz19c(self):
        # Envia el comando de lectura del sensor
        self.uart.write(self.buf)
        # Espera la respuesta del sensor
        time.sleep(0.1)
        if self.uart.any():
            # Verifica que la longitud de la respuesta sea la esperada (9 bytes)
            response = self.uart.read(9)
            if len(response) == 9:
                # Verifica que los primeros bytes de la respuesta sean correctos
                if response[0] == 0xFF and response[1] == 0x86:
                    # Calcula la concentración de CO2 a partir de los bytes 2 y 3
                    co2 = response[2] * 256 + response[3]
                    return co2 # nos devuelve en ppm
        # Si la respuesta no es válida o no hay datos, retorna None
        return None

    def send_sensor_data(self):
        co2_concentration = self.read_mhz19c()
        if co2_concentration is not None:
            data = {
                "topic": "sensor/co2",
                "value": co2_concentration
            }
            data_str = json.dumps(data)
            self.e.send(self.peer_mac, data_str)
            print("Mensaje enviado:", data_str)
        else:
            print("Failed to read from sensor")
        time.sleep(2)
            

# from sensor_mhz19c_uart import SensorMHZ19UART
#sensor1 = SensorMHZ19UART()
#sensor1.send_sensor_data()