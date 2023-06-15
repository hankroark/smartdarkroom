# Copyright 2023 Hank Roark
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
"""
Starts up the darkroom module, prints a welcome message, and makes it easy to get to the
default configured enlarger.
"""

import os

from gpiozero import LED
from smartdarkroom.enlarger import Enlarger

# This section configures the smartdarkroom, mostly by setting up the default enlarger
POWER_SWITCH_PIN = int(os.getenv('POWER_SWITCH_PIN', 18))
STARTUP_MESSAGE = os.getenv('STARTUP_MESSAGE', 'SMART DARKROOM 1.0.0 by Hank Roark')

switch = LED(POWER_SWITCH_PIN)  # Not really and LED, but it works like the LED API
enlarger = Enlarger(switch)

def main():
    """
    Prints the smartdarkroom startup message.
    """
    print(STARTUP_MESSAGE)

def get_enlarger():
    """
    Conveinence function to get the default enlarger so it can be added to the user REPL namespace.

    Returns:
        enlarger (smartdarkroom.enlarger.Enlarger): The default configured enlarger object.
    """
    return enlarger


if __name__ == "__main__":
    main()