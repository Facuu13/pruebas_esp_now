import time
from machine import Pin, I2C
import json
from config.network_espnow import SensorBase

class SensorHTU21(SensorBase):
    def __init__(self):
        super().__init__()
        #self.i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000) #ESP32
        self.i2c = I2C(0, scl=Pin(4), sda=Pin(5), freq=100000) #ESP32M1
        self.addr = 0x40 # Dirección del dispositivo HTU21 en el bus I2C

    def _read(self, cmd):
        # Envía un comando al sensor y lee los datos de respuesta
        self.i2c.writeto(self.addr, bytearray([cmd]))  # Envía el comando al sensor
        time.sleep(0.05)  # Espera para permitir que el sensor procese el comando
        data = self.i2c.readfrom(self.addr, 3)  # Lee 3 bytes de datos del sensor
        value = data[0] << 8 | data[1]  # Combina los dos primeros bytes para formar el valor
        value &= 0xFFFC  # Aplica una máscara para eliminar los bits menos significativos
        return value
    
    def temperature(self):
        # Lee y calcula la temperatura
        temp = self._read(0xE3)  # Lee el valor de temperatura del sensor
        temperatura = -46.85 + (175.72 * (temp / 65536.0))  # Convierte el valor leído a grados Celsius
        return round(temperatura, 2)  # Redondea el valor a dos decimales y lo devuelve
    
    def humidity(self):
        # Lee y calcula la humedad
        hum = self._read(0xE5)  # Lee el valor de humedad del sensor
        humedad = -6.0 + (125.0 * (hum / 65536.0))  # Convierte el valor leído a porcentaje de humedad
        return round(humedad, 2)  # Redondea el valor a dos decimales y lo devuelve
    
    def send_sensor_data(self):
        hum = self.humidity()
        time.sleep(0.1)
        temp = self.temperature()
        if hum and temp is not None:
            data = {
                "topic": "sensor/hum",
                "value": hum
            }
            data_str = json.dumps(data)
            self.e.send(self.peer_mac, data_str)
            print("Mensaje enviado:", data_str)
            
            time.sleep(1)
            
            data2 = {
                "topic": "sensor/temp",
                "value": temp
            }
            data2_str = json.dumps(data2)
            self.e.send(self.peer_mac, data2_str)
            print("Mensaje enviado:", data2_str)
            
        else:
            print("Failed to read from sensor")
        
# Ejemplo de uso
# from sensor_htu21 import SensorHTU21
#sensor = SensorHTU21()
#sensor.send_sensor_data()