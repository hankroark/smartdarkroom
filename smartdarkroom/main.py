import os

from gpiozero import LED
from smartdarkroom.enlarger import Enlarger

POWER_SWITCH_PIN = int(os.getenv('POWER_SWITCH_PIN', 18))
STARTUP_MESSAGE = os.getenv('STARTUP_MESSAGE', 'SMART DARKROOM 0.0.1 by Hank Roark')

switch = LED(POWER_SWITCH_PIN)
enlarger = Enlarger(switch)

def main():
    print(STARTUP_MESSAGE)

def get_enlarger():
    return enlarger


if __name__ == "__main__":
    main()