import sys
sys.path.append("")

from micropython import const
import uasyncio as asyncio
import aioble
import bluetooth
import struct

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)

# Helper to decode the temperature characteristic encoding (sint16, hundredths of a degree).
def _decode_temperature(data):
    return struct.unpack("<h", data)[0] / 100

async def find_temp_sensors():
    devices = []
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            # See if it matches our name and the environmental sensing service.
            if result.name() == "mpy-temp" and _ENV_SENSE_UUID in result.services():
                devices.append(result.device)
    return devices

async def handle_sensor(device):
    try:
        print("Connecting to", device)
        connection = await device.connect()
    except asyncio.TimeoutError:
        print("Timeout during connection to", device)
        return

    async with connection:
        try:
            temp_service = await connection.service(_ENV_SENSE_UUID)
            temp_characteristic = await temp_service.characteristic(_ENV_SENSE_TEMP_UUID)
        except asyncio.TimeoutError:
            print("Timeout discovering services/characteristics for", device)
            return

        while True:
            try:
                temp_deg_c = _decode_temperature(await temp_characteristic.read())
                print("Device:", device, "Temperature: {:.2f}".format(temp_deg_c))
                await asyncio.sleep_ms(1000)
            except Exception as e:
                print("Error reading temperature from", device, ":", e)
                break

async def main():
    devices = await find_temp_sensors()
    if not devices:
        print("No temperature sensors found")
        return

    tasks = [asyncio.create_task(handle_sensor(device)) for device in devices]
    await asyncio.gather(*tasks)

asyncio.run(main())
