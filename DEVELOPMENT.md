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

## Example of advanced feature 
Making a split grade f-stop print strip where the base low grade exposure has been determined.
Using this to show an example of how a bit of Python skills can make use of the base implementation
to do advanced features without them being in the base module.

```
import smartdarkroom.prints as p
from itertools import cycle, chain
baseExposure = p.OneExposurePrint(4, grade=0)
fstopStrip = p.FStopTestStrip(4, grade=5)
splitGradeTestStrip = p.PrintBase(list(chain.from_iterable(zip(cycle(baseExposure), fstopStrip))))
print(splitGradeTestStrip)

> PrintBase(
>    1: PrintStep(Exposure 4.0 sec, Grade 0, Place paper for print., No pre-step preview light),
>    2: PrintStep(Exposure 4.0 sec, Grade 5, , No pre-step preview light),
>    3: PrintStep(Exposure 4.0 sec, Grade 0, Place paper for print., No pre-step preview light),
>    4: PrintStep(Exposure 5.7 sec, Grade 5, , No pre-step preview light),
>    5: PrintStep(Exposure 4.0 sec, Grade 0, Place paper for print., No pre-step preview light),
>    6: PrintStep(Exposure 8.0 sec, Grade 5, , No pre-step preview light),
>    7: PrintStep(Exposure 4.0 sec, Grade 0, Place paper for print., No pre-step preview light),
>    8: PrintStep(Exposure 11.3 sec, Grade 5, , No pre-step preview light),
>    9: PrintStep(Exposure 4.0 sec, Grade 0, Place paper for print., No pre-step preview light),
>    10: PrintStep(Exposure 16.0 sec, Grade 5, , No pre-step preview light),
> Notes:
> )
```
