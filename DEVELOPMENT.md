# Notes for Developers of SmartDarkroom

## Setting up the python environment
Needs python 3.7 or greater

If developing on Mac or Windows: run `pip install -r requirements-dev.txt`.  
This will skip installing the RaspberryPi GPIO native libaries and allow development.

## Mocking the GPIO pins for development
SmartDarkroom uses the GPIO Zero library for implementation.  To use the mock GPIO pin implementation
from GPIO Zero, start SmartDarkroom with `GPIOZERO_PIN_FACTORY=mock ./smartdarkroom.sh`.  

## Control GPIO pin for enlarger
By default the GPIO pin to control the simple enlarger to be on or off is pin 18.  This can be changed
at startup by `POWER_SWITCH_PIN=16 ./smartdarkroom.sh`.  I often do this as I have a simple actual LED
hooked to that pin (with a resistor to ground) and I can test new functionality without flipping 
on and off the enlarger.
