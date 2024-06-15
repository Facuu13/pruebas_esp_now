import sys
sys.path.append("")

from micropython import const
import uasyncio as asyncio
import aioble
import bluetooth
import struct

# UUIDs
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
_ENV_SENSE_HUM_UUID = bluetooth.UUID(0x2A6F)

# Helper to decode the temperature characteristic encoding (sint16, hundredths of a degree).
def _decode_temperature(data):
    return struct.unpack("<h", data)[0] / 100

# Helper to decode the humidity characteristic encoding (sint16, hundredths of a percent).
def _decode_humidity(data):
    return struct.unpack("<h", data)[0] / 100

async def find_temp_hum_sensors():
    sensors = []
    # Scan for 5 seconds, in active mode, with very low interval/window (to maximize detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            # Check if the result matches the name pattern and the environmental sensing service.
            if (result.name().startswith("DHT11") or result.name().startswith("LM35")) and _ENV_SENSE_UUID in result.services():
                sensors.append(result.device)
    return sensors

async def connect_and_read_sensor(device):
    try:
        print("Connecting to", device)
        connection = await device.connect()
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return

    async with connection:
        try:
            temp_service = await connection.service(_ENV_SENSE_UUID)
            temp_characteristic = await temp_service.characteristic(_ENV_SENSE_TEMP_UUID)
            hum_characteristic = None
            if device.name().startswith("DHT11"):
                hum_characteristic = await temp_service.characteristic(_ENV_SENSE_HUM_UUID)
        except asyncio.TimeoutError:
            print("Timeout discovering services/characteristics")
            return

        while True:
            try:
                temp_deg_c = _decode_temperature(await temp_characteristic.read())
                if hum_characteristic:
                    hum_percent = _decode_humidity(await hum_characteristic.read())
                    print(f"Device: {device.name()}, Temperature: {temp_deg_c:.2f} °C, Humidity: {hum_percent:.2f} %")
                else:
                    print(f"Device: {device.name()}, Temperature: {temp_deg_c:.2f} °C")
            except Exception as e:
                print("Failed to read from sensor:", e)
            await asyncio.sleep_ms(1000)

async def main():
    sensors = await find_temp_hum_sensors()
    if not sensors:
        print("No temperature and humidity sensors found")
        return

    tasks = [asyncio.create_task(connect_and_read_sensor(device)) for device in sensors]
    await asyncio.gather(*tasks)

asyncio.run(main())
