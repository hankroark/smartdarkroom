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

import time
import os
import smartdarkroom.utils as sdutils
import smartdarkroom.prints
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

METRONOME_SOUND = os.getenv('METRONOME_SOUND', 'smartdarkroom/resources/metronome_click.wav')
AFTER_PREVIEW_SOUND = os.getenv("AFTER_PREVIEW_SOUND", 'smartdarkroom/resources/whistle.wav')

class Enlarger():
    def __init__(self, light):
        self.light = light
        self._filter = None
        self.light.off()

    def _focus_on(self):
        self.light.on()

    def _focus_off(self):
        self.light.off()

    def focus(self):
        try:
            self._focus_on()
            input("*** Press the ENTER key to turn off focus. ")
        finally:
            self._focus_off()

    def _set_filter(self, filter):
        if filter != self._filter:
            input(f"*** Set filter to {filter}.  Press ENTER when complete. ")
            self._filter = filter 
        
    def print(self, seconds, filter=None, before_print_seconds=0, before_print_light=False):
        self._set_filter(filter)

        try:
            if before_print_seconds > 0:
                print(f"Before print for {before_print_seconds:.1f} seconds w/light {before_print_light}")
                before_metro = Metronome()
                if before_print_light:
                    self.light.on()
                time.sleep(before_print_seconds)
                before_metro.stop()
                _play_after_preview_sound()

            print(f"Printing for {seconds:.1f} seconds")
            metronome = Metronome()
            self.light.on()
            time.sleep(seconds)
        finally:
            self.light.off()
            metronome.stop()

    def make(self, the_print):
        self._focus_off()  # turn off the focus if it is on
        self._preview_print(the_print)
        steps = the_print.get_print_list()
        for i, step in enumerate(steps):
            print(f"Step {i+1}: {step}")
            input(f"*** {step.user_prompt}  Press the ENTER when complete. ")
            self.print(step.duration, step.grade, step.before_step_duration, step.before_step_light)

    def _preview_print(self, the_print):
        print("### PRINT STRATEGY PREVIEW ###")
        print(the_print)
        print("### END PRINT STRATEGY PREVIEW ###")
        print("")

class Metronome():
    def __init__(self, sound = METRONOME_SOUND, interval = 1):
        pygame.mixer.init()
        self._count = 0
        self._metronome_sound=pygame.mixer.Sound(sound)
        self._metronome = sdutils.RepeatedTimer(interval, self._play)

    def _play(self):
        pygame.mixer.Sound.play(self._metronome_sound)

        if self._count == 0:
            print("TIMER: ", end="", flush=True)
        else:
            print("\b\b\b", end="", flush=True)

        print(f"{self._count:02} ", end="", flush=True)
        self._count += 1

    def start(self):
        self._metronome.start()

    def stop(self):
        self._metronome.stop()
        print("", flush=True)

def _play_after_preview_sound(sound = AFTER_PREVIEW_SOUND, repeat=2):
    pygame.mixer.init()
    after_preview_sound = pygame.mixer.Sound(sound)
    for _ in range(repeat):
        pygame.mixer.Sound.play(after_preview_sound)