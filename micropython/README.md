# DCF77 faker for ESP32 micropython

It is connected to series LC resonant circuit
with ferrite core, tuned to 77.5 kHz approx.

For precise frequency, RMT module is used to
generate the PWM signal because PWM module is not
accurate enough for 77.5 kHz carrier frequency.

Amplitude modulation is done by driving LC resonant
circuit with 55% reduced duty cycle, on the scope it
is measured as 15% amplitude reduction.

Summary:

Frequency: 77.4994 kHz
Modulation: -15% of carrier amplitude
0 time: 100ms, 1 time: 200ms, each second.

But DCF77 clocks don't recognize this signal
no idea why ...
