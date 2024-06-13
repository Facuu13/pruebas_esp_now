import sys
sys.path.append("")

from micropython import const
import uasyncio as asyncio
import aioble
import bluetooth
import dht
import machine
import struct

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
# org.bluetooth.characteristic.humidity
_ENV_SENSE_HUM_UUID = bluetooth.UUID(0x2A6F)
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)

# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250_000

# Setup DHT11 sensor
dht_pin = machine.Pin(2)  # Adjust pin number according to your setup
dht_sensor = dht.DHT11(dht_pin)

# Register GATT server.
temp_service = aioble.Service(_ENV_SENSE_UUID)
temp_characteristic = aioble.Characteristic(
    temp_service, _ENV_SENSE_TEMP_UUID, read=True, notify=True
)
hum_characteristic = aioble.Characteristic(
    temp_service, _ENV_SENSE_HUM_UUID, read=True, notify=True
)
aioble.register_services(temp_service)

# Helper to encode the temperature characteristic encoding (sint16, hundredths of a degree).
def _encode_temperature(temp_deg_c):
    return struct.pack("<h", int(temp_deg_c * 100))

# Helper to encode the humidity characteristic encoding (sint16, hundredths of a percent).
def _encode_humidity(hum_percent):
    return struct.pack("<h", int(hum_percent * 100))

# This would be periodically polling a hardware sensor.
async def sensor_task():
    while True:
        try:
            dht_sensor.measure()
            temp = dht_sensor.temperature()
            hum = dht_sensor.humidity()
            temp_characteristic.write(_encode_temperature(temp))
            hum_characteristic.write(_encode_humidity(hum))
            print(f"Temperature: {temp:.2f} °C, Humidity: {hum:.2f} %")
        except OSError as e:
            print("Failed to read from DHT sensor:", e)
        await asyncio.sleep_ms(1000)

# Serially wait for connections. Don't advertise while a central is connected.
async def peripheral_task():
    while True:
        async with await aioble.advertise(
            _ADV_INTERVAL_MS,
            name="mpy-temp",
            services=[_ENV_SENSE_UUID],
            appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER,
        ) as connection:
            print("Connection from", connection.device)
            await connection.disconnected()

# Run both tasks.
async def main():
    t1 = asyncio.create_task(sensor_task())
    t2 = asyncio.create_task(peripheral_task())
    await asyncio.gather(t1, t2)

asyncio.run(main())
