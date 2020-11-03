# DCF77 faker for ESP32 micropython

It is connected to series LC resonant circuit
with ferrite core, tuned to 77.5 kHz approx.

Using RMT module, signal is adjusted at the source
and results measured with the scope.

Frequency is 77.4994 kHz

amplitude modulation is done by PWM driving LC resonant
circuit, on the scope it can be measured as 15% amplitude reduction.

Each second it sends 0 for 100ms, 1 for 200ms.

But DCF77 clocks don't recognize this signal
no idea why ...
