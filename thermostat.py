"""Mini BAS controller on a Raspberry Pi.

Reads a DHT11 temperature/humidity sensor and switches an LED output with a
setpoint and deadband.

Wiring (physical header pins):
    DHT11 VCC  -> pin 1 (3.3V)
    DHT11 DATA -> pin 7 (GPIO4), with a 10k pull-up to VCC on the bare 4-pin sensor
    DHT11 GND  -> pin 9 (GND)
    LED anode  -> 220 ohm resistor -> pin 12 (GPIO18)
    LED cathode -> pin 9 (GND)
"""

import time

import adafruit_dht
import board
from gpiozero import LED

# --- Settings ---
SETPOINT_F = 75.0
DEADBAND_F = 2.0         # DHT11 steps are about 1.8 F, so keep this at 2 or more
TEMP_OFFSET_F = -3.0     # calibration offset: reference thermometer minus sensor reading
READ_INTERVAL_S = 2      # DHT11 can only be read about once per second at best

dht = adafruit_dht.DHT11(board.D4)   # data on GPIO4 (physical pin 7)
led = LED(18)                        # output on GPIO18 (physical pin 12)


def read_sensor():
    """Return (temp_f, humidity), or (None, None) on a bad read."""
    try:
        temp_c = dht.temperature
        humidity = dht.humidity
        if temp_c is None or humidity is None:
            return None, None
        return temp_c * 9 / 5 + 32 + TEMP_OFFSET_F, humidity
    except RuntimeError:
        # DHT sensors miss reads often (checksum or timing errors). Skip and retry.
        return None, None


try:
    while True:
        temp_f, humidity = read_sensor()
        if temp_f is None:
            print("Bad read, skipping")
        else:
            # Cooling output: ON above setpoint + deadband, OFF below setpoint - deadband.
            # Inside the deadband the output holds its last state.
            if temp_f > SETPOINT_F + DEADBAND_F:
                led.on()
            elif temp_f < SETPOINT_F - DEADBAND_F:
                led.off()
            state = "ON" if led.is_lit else "OFF"
            print(f"Temp: {temp_f:.1f} F  Humidity: {humidity}%  Output: {state}")
        time.sleep(READ_INTERVAL_S)
except KeyboardInterrupt:
    pass
finally:
    led.off()
    dht.exit()
