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
# org.bluetooth.characteristic.humidity
_ENV_SENSE_HUM_UUID = bluetooth.UUID(0x2A6F)

# Helper to decode the temperature characteristic encoding (sint16, hundredths of a degree).
def _decode_temperature(data):
    return struct.unpack("<h", data)[0] / 100

# Helper to decode the humidity characteristic encoding (sint16, hundredths of a percent).
def _decode_humidity(data):
    return struct.unpack("<h", data)[0] / 100

async def find_temp_hum_sensor():
    # Scan for 5 seconds, in active mode, with very low interval/window (to maximize detection rate).
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            # See if it matches our name and the environmental sensing service.
            if result.name() == "sensor-1" and _ENV_SENSE_UUID in result.services():
                return result.device
    return None

async def main():
    device = await find_temp_hum_sensor()
    if not device:
        print("Temperature and humidity sensor not found")
        return

    try:
        print("Connecting to", device)
        connection = await device.connect()
    except asyncio.TimeoutError:
        print("Timeout during connection")
        return
    except Exception as e:
        print("Connection failed:", e)
        return

    async with connection:
        try:
            temp_service = await connection.service(_ENV_SENSE_UUID)
            temp_characteristic = await temp_service.characteristic(_ENV_SENSE_TEMP_UUID)
            hum_characteristic = await temp_service.characteristic(_ENV_SENSE_HUM_UUID)
        except asyncio.TimeoutError:
            print("Timeout discovering services/characteristics")
            return
        except Exception as e:
            print("Failed to discover services/characteristics:", e)
            return

        while True:
            try:
                temp_deg_c = _decode_temperature(await temp_characteristic.read())
                hum_percent = _decode_humidity(await hum_characteristic.read())
                print("Temperature: {:.2f} °C, Humidity: {:.2f} %".format(temp_deg_c, hum_percent))
            except Exception as e:
                print("Failed to read from sensor:", e)
            await asyncio.sleep_ms(1000)

asyncio.run(main())
