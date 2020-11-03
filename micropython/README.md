# ESP32 as DCF77 transmitter (micropython)

Series LC resonant circuit is tuned to 77.5 kHz.
LC circuit consits of a coil wound on a ferrite core
and a 4.7nF capacitor, chosen among many to best fit
for 77.5 kHz.
LC circuit is connected to ESP32 between
GPIO15 and GND.

For precise frequency, ESP32 RMT module is used to
generate the PWM signal because standard PWM module is not
accurate enough to generate precise 77.5 kHz carrier frequency.

Amplitude modulation is done by driving LC resonant
circuit with 2 different duty cycles, about 50% DTC
for unmodulated carrier and about 12% DTC for modulated
carrier with 25% reduced amplitude while sending 0 or 1.

Frequency and amplitude modulation is measured with oscilloscope
connected to 3-turn wire as probe coil placed near the LC circuit.
Tuning paramters are adjusted when measured with the scope.
