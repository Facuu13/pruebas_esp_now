import sys
sys.path.append("")

from micropython import const
import uasyncio as asyncio
import aioble
import bluetooth
import dht
import machine
import struct

# UUIDs
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
_ENV_SENSE_HUM_UUID = bluetooth.UUID(0x2A6F)
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)
_ADV_INTERVAL_MS = 250_000

# Setup DHT11 sensor
dht_pin = machine.Pin(32)
dht_sensor = dht.DHT11(dht_pin)

# Register GATT server.
temp_service = aioble.Service(_ENV_SENSE_UUID)
temp_characteristic = aioble.Characteristic(temp_service, _ENV_SENSE_TEMP_UUID, read=True, notify=True)
hum_characteristic = aioble.Characteristic(temp_service, _ENV_SENSE_HUM_UUID, read=True, notify=True)
aioble.register_services(temp_service)

def _encode_temperature(temp_deg_c):
    return struct.pack("<h", int(temp_deg_c * 100))

def _encode_humidity(hum_percent):
    return struct.pack("<h", int(hum_percent * 100))

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

async def peripheral_task(sensor_id):
    while True:
        async with await aioble.advertise(
            _ADV_INTERVAL_MS,
            name=f"sensor-{sensor_id}",
            services=[_ENV_SENSE_UUID],
            appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER,
        ) as connection:
            print("Connection from", connection.device)
            await connection.disconnected()

async def main():
    sensor_id = 1  # Change this ID for each sensor
    t1 = asyncio.create_task(sensor_task())
    t2 = asyncio.create_task(peripheral_task(sensor_id))
    await asyncio.gather(t1, t2)

asyncio.run(main())
