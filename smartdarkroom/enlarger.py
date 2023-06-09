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
This module encapsulates the notion of what an enlarger should be.  Right now it
represents a simple enlarger with on/off, a filter, a metronome, and a count-up
clock for prints.  It can run a single print, or run a whole strategy of print
steps as defined from the smartdarkroom.prints module.
"""

import time
import os
import smartdarkroom.utils as sdutils
import smartdarkroom.prints
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from itertools import tee
import logging
import logging.config


METRONOME_SOUND = os.getenv('METRONOME_SOUND', 'smartdarkroom/resources/metronome_click.wav')
AFTER_PREVIEW_SOUND = os.getenv("AFTER_PREVIEW_SOUND", 'smartdarkroom/resources/whistle.wav')

# load the logging config file
logging.config.fileConfig('smartdarkroom/logging.conf')
# create logger
enlargerLogger = logging.getLogger('enlargerLogger')

class Enlarger():
    """
    Represents a basic enlarger.  There is a light that can be turned on and off, there is a filter setting,
    and in this case can run the strategy represented by a print.
    """
    
    def __init__(self, light):
        """
        Constructs a new instance of the Enlarger.  Sets light to off, and clears the filter to None.

        Parameters:
            light: Required. An object that takes the funtions of on() and off() to control the light in the enlarger.
        """
        self._light = light
        self._filter = None
        self._off()

    def _on(self):
        """
        Turns on the light on the enlarger.
        """
        self._light.on()

    def _off(self):
        """
        Turns off the light on the enlarger
        """
        self._light.off()

    def focus(self, timeout=300):
        """
        Turns on the light of the enlarger so user can focus or do other operations.
        Waits for the user to press the Enter key to turn off the light.

        Parameters:
            timeout: Auto turn off the enlarger after timeout seconds. Default 300 (5 minutes)
        """
        try:
            with sdutils.Timeout(seconds=timeout):
                self._on()
                input("*** Press the ENTER key to turn off focus. ")
        except TimeoutError:
            print("\nReached focus timeout, turning off enlarger to protect bulb")
        finally:
            self._off()

    def _set_filter(self, filter):
        """
        Sets the filter of the enlarger.  This assumes the user of the enlarger has to set
        the filter, so it commands the user to set the filter and to confirm by hitting Enter.
        
        Parameters:
            filter: Required. Anything object that can be compared with == to prior filter to determine state of the enlarger"""
        if filter != self._filter:
            input(f"*** Set filter to {filter}.  Press ENTER when complete.")
            self._filter = filter 
    
    def print(self, seconds, *, filter=None):
        """
        This is the most basic print command.  It turns on the enlarger for a certain number of seconds.
        There are options to set the filter.  A metronome will sound every second.


        Parameters:
            seconds (float): Required. The number of seconds for the print.

        Keyword Parameters:
            filter: The filter to be set on the enlarger for the print.
        """
        self._print(seconds, filter=filter)

    def _print(self, seconds, *, filter=None, before_print_seconds=0, turn_off_enlarger_at_end_of_print=True):
        """
        This is the core implementation of a print step command.  It turns on the enlarger for a certain number of seconds.
        There are options to set the filter.  A metronome will sound every second.
        As well there is a preview light that can be turned on to help the user setup for dodge or 
        burn operations; a metronome will also sound during this time and will sound a bell at the end
        of the preview light duration.

        Parameters:
            seconds (float): Required. The number of seconds for the print.

        Keyword Parameters:
            filter: The filter to be set on the enlarger for the print.
            before_print_seconds (float): If using the preview light the number of seconds for it to be on. Default to 0.
            turn_off_enlarger_at_the_end_of_print (boolean): Says if the enlarger should stay on after the print time.  
                Usually only set to False for dodge steps following the main print.  Default True.
        """
        self._set_filter(filter)

        try:
            if before_print_seconds > 0:
                print(f"Before print for {before_print_seconds:.1f} seconds w/light.")
                before_metro = Metronome()
                self._on()
                time.sleep(before_print_seconds)
                before_metro.stop()
                _play_after_preview_sound()
            elif before_print_seconds < 0:   # Give the user a audible warning if there was no pause at all
                _play_after_preview_sound()

            print(f"Printing for {seconds:.1f} seconds")
            actual_seconds = float(f"{seconds:.1f}")  # print what you tell the user
            metronome = Metronome()
            self._on()
            time.sleep(actual_seconds)
        finally:
            # Don't turn the enlarger off if there is no pause for the next step
            if turn_off_enlarger_at_end_of_print:
                self._off()
            time.sleep(0.01) # 1/100th second delay so metronome is dispaly correctly
            metronome.stop()

    def make(self, the_print):
        """
        This runs a series of print steps as represented in a smartdarkroom.prints.PrintBase object.
        The user will get a preview of all the steps getting ready to execute, and asked to hit 
        Enter before each step starts.  If the focus light is on, it will auto be turned off at the
        beginning of the sequence.

        Parameters:
            the_print (smartdarkroom.prints.PrintBase):  The print to execute
        """
        self._off()  # turn off the focus if it is on
        self._preview_print(the_print)
        steps = the_print.get_print_list()

        # Get me the list of steps twice
        steps_main, steps_lookahead = tee(steps)
        # Skip to the next step for the b list
        next(steps_lookahead, None)
        # for i, step in enumerate(steps):
        for step_number, step in enumerate(steps_main):
            print(f"Step {step_number+1}: {step}")

            # Don't prompt the user unless the step says to pause
            if step.before_step_duration >= 0:
                input(f"*** {step.user_prompt}  Press the ENTER when ready to continue.")
            
            # Look ahead at the next step and see if they want the enlarger left on for them
            next_step = next(steps_lookahead, None)
            turn_off_enlarger_at_end_of_step = True # default
            if next_step is not None:
                turn_off_enlarger_at_end_of_step = next_step.before_step_duration >= 0

            self._print(step.duration, filter=step.grade, before_print_seconds=step.before_step_duration, turn_off_enlarger_at_end_of_print=turn_off_enlarger_at_end_of_step)

        enlargerLogger.info("Completed print")
        enlargerLogger.info(the_print)
        enlargerLogger.info("End of print details")

    def _preview_print(self, the_print):
        """
        This displays all the steps of the print so the user will know what all is coming up.

        Parameters:
            the_print (smartdarkroom.prints.BasicPrint):  The print to show the user the upcoming steps
        """
        print("### PRINT STRATEGY PREVIEW ###")
        print(the_print)
        print("### END PRINT STRATEGY PREVIEW ###")
        print("")

class Metronome():
    """
    This is mostly a hidden class, meant to add a metronome to enlargers that don't have that built in.
    It also displays a timer of the number of seconds the metronome has been running.  This will help
    users see how much of a particular print step has execute.
    """

    def __init__(self, sound = METRONOME_SOUND, interval = 1):
        pygame.mixer.init()
        self._count = 0
        self._sound_interval = interval
        self._display_interval = interval / 10
        self._metronome_sound=pygame.mixer.Sound(sound)
        self._metronome = sdutils.RepeatedTimer(self._display_interval, self._play)

    def _play(self):
        if self._count % 10 == 0:
            pygame.mixer.Sound.play(self._metronome_sound)

        if self._count == 0:
            print("TIMER: ", end="", flush=True)
        else:
            print("\b\b\b\b", end="", flush=True)

        print(f"{self._count / 10:4.1f}", end="", flush=True)
        self._count += 1

    def start(self):
        self._metronome.start()

    def stop(self):
        self._metronome.stop()
        print("", flush=True)

def _play_after_preview_sound(sound = AFTER_PREVIEW_SOUND, repeat=2):
    """
    Function to play a bell sound (or any configurable sound) after the preview light is shown.
    """
    pygame.mixer.init()
    after_preview_sound = pygame.mixer.Sound(sound)
    for _ in range(repeat):
        pygame.mixer.Sound.play(after_preview_sound)

