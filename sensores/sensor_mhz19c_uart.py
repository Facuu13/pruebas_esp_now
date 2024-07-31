import time
from machine import UART, Pin
import json
from network_espnow import SensorBase

class SensorMHZ19(SensorBase):
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
            response = self.uart.read(9)
            if len(response) == 9:
                if response[0] == 0xFF and response[1] == 0x86:
                    co2 = response[2] * 256 + response[3]
                    return co2 # nos devuelve en ppm
        return None

    def send_sensor_data(self):
        co2_concentration = self.read_mhz19c()
        data = {
            "topic": "sensor/co2",
            "value": co2_concentration
        }
        data_str = json.dumps(data)
        self.e.send(self.peer_mac, data_str)
        print("Mensaje enviado:", data_str)
        time.sleep(2)
            

# from sensor_mhz19c_uart import SensorMHZ19
#sensor = SensorMHZ19()
#sensor.send_sensor_data()