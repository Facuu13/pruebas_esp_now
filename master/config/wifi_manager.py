import network
import time
import json
import ntptime
import machine

class WiFiManager:
    def __init__(self, config_path='config/config.json'):
        self.config = self.cargar_configuracion(config_path)
        self.sta, self.ap = self.wifi_reset()
        self.conectado_wifi = False
        self.iniciar_wifi()
    
    def cargar_configuracion(self, config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    
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
    
    def iniciar_wifi(self):
        modo = self.config.get("mode", "CL")
        if modo == "CL":
            self.conectar_wifi()
        elif modo == "AP":
            self.iniciar_modo_ap()
        else:
            print("Modo no reconocido. Iniciando en modo cliente por defecto.")
            self.conectar_wifi()

    def conectar_wifi(self):
        ssid = self.config.get("ssid")
        password = self.config.get("password")
        self.sta.connect(ssid, password)
        print("Conectando cliente WiFi a:", ssid)
        while True:
            if (self.sta.status() == network.STAT_CONNECTING):
                print(".", end='')
                time.sleep(1)
            elif (self.sta.status() == network.STAT_WRONG_PASSWORD):
                print("Contraseña incorrecta")
                self.cambiar_a_modo_ap()
                break
            elif (self.sta.status() == network.STAT_NO_AP_FOUND):
                print("Red no encontrada")
                self.cambiar_a_modo_ap()
                break
            elif (self.sta.status() == network.STAT_GOT_IP):
                print("Conexion exitosa")
                print("Dirección IP:", self.sta.ifconfig()[0])
                self.conectado_wifi = True
                self.set_rtc_from_ntp()
                break
            else:
                print("Error al conectar")
                print("Status:", self.sta.status())
                self.conectado_wifi = False
                break
        
        self.sta.config(pm=self.sta.PM_NONE)
        print("Proxy corriendo en el canal:", self.sta.config("channel"))

    def cambiar_a_modo_ap(self):
        print("Cambiando a modo AP")
        self.conectado_wifi = False
        self.iniciar_modo_ap()
        

    def iniciar_modo_ap(self):
        ap_ssid = self.config.get("ap_ssid", "ESP32_AP")
        ap_password = self.config.get("ap_password", "12345678")
        self.ap.active(True)
        self.ap.config(essid=ap_ssid, password=ap_password,authmode=network.AUTH_WPA2_PSK)
        print("Punto de acceso iniciado")
        print("SSID:", ap_ssid)
        print("Contraseña:", ap_password)
        print(self.ap.ifconfig())
        self.set_rtc_from_json() #setear hora del rtc

    
    def set_rtc_from_json(self):
        """
        Sincroniza la hora del RTC desde el archivo JSON (modo AP).
        """
        try:
            rtc = machine.RTC()
            rtc.datetime((self.config['year'], self.config['month'], self.config['day'], 0, self.config['hour'], self.config['minute'], self.config['second'], 0))
            print("RTC configurado desde archivo JSON")
        except Exception as e:
            print("Error al configurar RTC desde archivo JSON:", e)

    def set_rtc_from_ntp(self):
        """
        Sincroniza la hora del RTC usando el servidor NTP de Google.
        Ajusta la hora a la zona horaria de Argentina (UTC-3).
        """
        try:
            print("Sincronizando con NTP...")
            
            # Configuramos el servidor NTP 
            ntptime.host = "time.google.com"
            
            # Sincronizamos la hora
            ntptime.settime()
            
            # Obtenemos la hora actual del RTC y ajustamos UTC-3
            rtc = machine.RTC()
            fecha_hora = list(rtc.datetime())
            
            # Ajustar la hora para UTC-3 (restar 3 horas)
            fecha_hora[4] = (fecha_hora[4] - 3) % 24  # Ajustar la hora

            # Si se cruza la medianoche, ajustar también el día
            if fecha_hora[4] > rtc.datetime()[4]:
                fecha_hora[2] -= 1  # Restar un día si cruzamos medianoche
            
            # Aplicar el nuevo datetime ajustado
            rtc.datetime(tuple(fecha_hora))

            print("Hora sincronizada desde Argentina NTP:", rtc.datetime())
        except Exception as e:
            print("Error al sincronizar RTC desde NTP:", e)


    def devolver_hora_actual(self):
        """
        Devuelve la hora actual del RTC.
        """
        # x es dia de la semana, que no se usa
        rtc = machine.RTC()
        anio, mes, dia,x, hora, minuto, segundo, *_ = rtc.datetime()
        hora_actual = f"Hora actual: {dia}/{mes}/{anio} {hora}:{minuto}:{segundo}"
        return hora_actual