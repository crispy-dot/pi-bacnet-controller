# Raspberry Pi Controller: Point-to-Point Checkout

Mini controller on a Raspberry Pi 4: DHT11 temperature/humidity sensor (GPIO4, pin 7) and an LED output (GPIO18, pin 12), with setpoint and deadband control in `thermostat.py`.

**Reference instrument:** Fluke meter (fill in model) for temperature
**Settings under test:** setpoint 75 F then 80 F, deadband 2 F

## Results

| Point | Type | Test | Expected | Actual | Result |
|---|---|---|---|---|---|
| Room temperature | AI | Compare with reference | Within DHT11 spec (+/-2 C, about +/-3.6 F) | Reference 70 F, DHT11 73 F (+3 F) | Pass (within spec) |
| Humidity | AI | Breathe near sensor, then let it recover | Reading rises, then falls back | 25% to 69%, back to 30% | Pass |
| Setpoint | AV | Change setpoint to 80 F, rerun | Output switches around the new setpoint | LED turned on at 82 F | Pass |
| Output command | BO | Temperature above setpoint + deadband | LED on | LED on at 82 F | Pass |
| Output command | BO | Temperature below setpoint - deadband | LED off | LED off as soon as temp dropped below 78 F | Pass |
| Deadband | | Hold temperature inside the band | LED keeps previous state, no flicker | Held state, no flicker | Pass |
| Bad-read handling | | Briefly disconnect DATA wire | "Bad read" printed, no crash, LED holds state | No crash, LED held state | Pass |
| Cleanup on exit | | Ctrl+C with LED on | LED turns off | LED turned off | Pass |

## Meter checks (fill in)

| Measurement | Expected | Actual | Result |
|---|---|---|---|
| Pin 1 to ground (3.3V rail) | about 3.3 V | 3.306 V | Pass |
| DATA line, idle between reads | about 3.3 V (pull-up working) | 3.3 V idle, dips to about 3.0 V during reads | Pass (dip is the meter averaging the read pulses) |
| Pin 12 (GPIO18) to ground, LED on, pin side of resistor | about 3.1 to 3.3 V | 3.1 V after fix (2.1 V before fix) | Pass after fix |
| Pin 12 (GPIO18) to ground, LED off | about 0 V | 0 V | Pass |
| Across the LED (anode to cathode), LED on | about 1.9 to 2.1 V | 1.9 V | Pass |
| Across the 220 ohm resistor, LED on | about 1.1 to 1.2 V (about 5 mA) | 1.1 V (about 5 mA) | Pass |

## Calibration

| Reference | Sensor | Offset (reference minus sensor) |
|---|---|---|
| 70 F | 73 F | -3.0 F (`TEMP_OFFSET_F = -3.0`) |

One-point calibration at room temperature. The DHT11 reports whole degrees C, so readings move in steps of about 1.8 F.

## Notes

- Overrides and test changes were reverted: setpoint returned to its normal value and the DATA wire was reconnected.
- Limitations: DHT11 accuracy is about +/-2 C and 1 C resolution, so it is suited to learning and checkout practice, not precision control.

## Fault found during checkout

- **Symptom:** with the LED on, the pin side of the resistor and the LED both measured 2.1 V, so almost no voltage was dropping across the resistor.
- **Cause:** the pin 12 jumper shared a breadboard column group with the LED-side resistor leg, which bypassed the resistor.
- **Fix:** moved the jumper so the resistor's legs sit in separate column groups.
- **Verified after fix:** 3.1 V at the pin side, 1.1 V across the resistor (about 5 mA at 220 ohms), 1.9 V across the LED. The drops add up to about the pin voltage.
