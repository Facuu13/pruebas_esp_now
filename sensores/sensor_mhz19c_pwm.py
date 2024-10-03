import time
from machine import Pin, time_pulse_us
import json
from config.network_espnow import SensorBase

modelo = 'MHZ19C'
class SensorMHZ19PWM(SensorBase):
    def __init__(self):
        super().__init__()
        #self.pwm_pin = Pin(4, Pin.IN) #ESP32
        self.pwm_pin = Pin(3, Pin.IN) #ESP32C3M1
    
    def read_co2_pwm(self):
        try:
            # Medir tiempo en alto (TH)
            high_time = time_pulse_us(self.pwm_pin, 1)
            if high_time < 0:
                raise ValueError("Error en la medición de tiempo en alto")
            # Medir tiempo en bajo (TL)
            low_time = time_pulse_us(self.pwm_pin, 0)
            if low_time < 0:
                raise ValueError("Error en la medición de tiempo en bajo")
            # Verificar tiempos razonables
            if high_time < 2000 or low_time < 2000:
                raise ValueError("Tiempos fuera de rango esperado")
            # Calcular la concentración de CO2
            co2_concentration = 2000 * (high_time - 2000) / (high_time + low_time - 4000)
            return co2_concentration
        except ValueError as e:
            print("Error en la lectura del sensor:", e)
            return None
    
    def send_sensor_data(self):
        co2_concentration = self.read_co2_pwm()
        if co2_concentration is not None:

            value = str(co2_concentration) + " ppm"

            data = {
                "topic": "sensor/co2",
                "value": value,
                "modelo": modelo
            }
            self.send_encrypted_data(data)
            print("Datos del sensor enviados:", data)
        else:
            print("Failed to read from sensor")
        time.sleep(1)
        
# from sensor_mhz19c_pwm import SensorMHZ19PWM
#sensor2 = SensorMHZ19PWM()
#sensor2.send_sensor_data()

