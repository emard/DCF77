# ESP32 as DCF77 transmitter (micropython)

Series LC resonant circuit is tuned to 77.5 kHz.
Coil is wound on a ferrite core
and some capacitor chosen for example:

L=4.22mH + C=1nF or L=0.96mH + C=4.7nF

LC resonant frequency can be fine-tuned by positioning the coil
on the ferrite core. Frequency is lowest when coil is at the middle
of the ferrite core. When coil is moved to a side, frequency will
be slighty higher.

At resonance, quality of LC circuit is described by Q factor:

    Q = Voltage_accross_L/Voltage_source

Typical Q = 10-50 for ferrite LC so the voltage accross coil L
can be 30-150Vpp when driven with 3.3Vpp source. The signal can
reach few meters and cover one average room, but can't
reach thru multiple rooms.

LC circuit is connected to ESP32 between
GPIO15 and GND. 3.6V zener diode is for
protection, to prevent high voltage
from high Q LC circuit to return to the pin when
ESP32 is suddenly turned off.

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


# Installation

Copy "dcf77.py", "dst.py", "ssd1306.py", "wifiman.py" and
to root "/" of ESP32 flash or to "/lib" directory (it's the same).
Edit "wifiman.conf" change passwords and copy to root "/" of ESP32.
For autostart, at end of "main.py" after network is up,
add this line:

    import dcf77

# Daylight Saving Time

ESP32 can't hold large database of timezones.
In the file "dst.py" is a simple calculation
of daylight saving time for central europe.
Edit this to your preference.

# Requirements

Micropython 1.13 or higer (from esp32 import RMT)
