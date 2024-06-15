import sys
sys.path.append("")

from micropython import const
import uasyncio as asyncio
import aioble
import bluetooth
import machine
import struct

# UUIDs
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)
_ADV_INTERVAL_MS = 250_000

# Setup LM35 sensor
adc_pin = machine.ADC(machine.Pin(32))

def read_temperature():
    return adc_pin.read() * 3.3 / 4095 * 100  # Convert ADC value to temperature

# Register GATT server.
temp_service = aioble.Service(_ENV_SENSE_UUID)
temp_characteristic = aioble.Characteristic(temp_service, _ENV_SENSE_TEMP_UUID, read=True, notify=True)
aioble.register_services(temp_service)

def _encode_temperature(temp_deg_c):
    return struct.pack("<h", int(temp_deg_c * 100))

async def sensor_task():
    while True:
        try:
            temp = read_temperature()
            temp_characteristic.write(_encode_temperature(temp))
            print(f"Temperature: {temp:.2f} °C")
        except OSError as e:
            print("Failed to read from LM35 sensor:", e)
        await asyncio.sleep_ms(1000)

async def peripheral_task(sensor_id):
    while True:
        async with await aioble.advertise(
            _ADV_INTERVAL_MS,
            name=f"LM35-{sensor_id}",
            services=[_ENV_SENSE_UUID],
            appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER,
        ) as connection:
            print("Connection from", connection.device)
            await connection.disconnected()

async def main():
    sensor_id = 2  # Change this ID for each sensor
    t1 = asyncio.create_task(sensor_task())
    t2 = asyncio.create_task(peripheral_task(sensor_id))
    await asyncio.gather(t1, t2)

asyncio.run(main())
