# Usa la imagen oficial de Mosquitto
FROM eclipse-mosquitto:2

# Expone el puerto 1883 para MQTT
EXPOSE 1883

# Expone el puerto 9001 para Websockets (opcional)
EXPOSE 9001

# Copia el archivo de configuración (si lo tienes)
COPY mosquitto.conf /mosquitto/config/mosquitto.conf

# Ejecuta Mosquitto
CMD ["/usr/sbin/mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]
