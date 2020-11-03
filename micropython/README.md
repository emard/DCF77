# DCF77 faker for ESP32 micropython

It is connected to series LC resonant circuit
with ferrite core, tuned to 77.5 kHz approx.

Using RMT module, signal is adjusted and checked
on scope, frequency is 77.4994 kHz, amplitude
modulation is reduced 15% during sending 0 or 1,

But DCF77 clocks don't recognize this signal
no idea why ...
