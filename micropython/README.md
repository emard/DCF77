# ESP32 as DCF77 transmitter (micropython)

Series LC resonant circuit is tuned to 77.5 kHz.
Coil is wound on a ferrite core
and some capacitor chosen for example:

L=4.22mH + C=1nF or L=0.96mH + C=4.7nF

LC circuit is connected to ESP32 between
GPIO15 and GND. 3.6V zener diode is for
protection, not neccessary but recommended.

![LC circuit](/pic/LC.png)

For precise frequency, ESP32 RMT module is used to
generate the PWM signal because standard PWM module is not
accurate enough to generate exactly 77.5 kHz carrier frequency.

Amplitude modulation is done by driving LC resonant
circuit with 2 different duty cycles, about 50% DTC
for unmodulated carrier and about 12% DTC for modulated
carrier with 25% reduced amplitude while sending 0 or 1.

Frequency and amplitude modulation is measured with oscilloscope
connected to 3-turn wire as probe coil placed near the LC circuit.
Tuning paramters are adjusted when measured with the scope.

At resonance the voltage accross coil is 15-20V when driven
with 3.3V source. The signal can reach few meters
and cover one average room, but can't reach over several
rooms.

# Daylight Saving Time

ESP32 can't hold large database of timezones, so
here is small file "dst.py" with simple calculation
of daylight saving time for central europe.
Edit this to your preference.

# Requirements

Micropython 1.13 or higer (from esp32 import RMT)
