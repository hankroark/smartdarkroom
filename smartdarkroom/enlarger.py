import time
import os
import smartdarkroom.utils as sdutils
import smartdarkroom.prints
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

METRONOME_SOUND = os.getenv('METRONOME_SOUND', 'smartdarkroom/resources/metronome_click.wav')


class Enlarger():
    def __init__(self, light):
        self.light = light
        self.light.off()

    def _focus_on(self):
        self.light.on()

    def _focus_off(self):
        self.light.off()

    def focus(self):
        try:
            self._focus_on()
            input("Press the ENTER key to turn off focus")
        finally:
            self._focus_off()

    def print(self, seconds):
        try:
            print(f"Printing for {seconds:.1f} seconds")
            metronome = Metronome()
            self.light.on()
            time.sleep(seconds)
        finally:
            self.light.off()
            metronome.stop()

    def make(self, the_print):
        self._focus_off()  # turn off the focus if it is on
        steps = the_print.get_print_list()
        for step in steps:
            duration = step.duration
            print(step.user_prompt)
            print(f"Will print {duration:.1f} seconds")
            input("Press the ENTER key to continue...")
            self.print( duration )


class Metronome():
    def __init__(self, sound = METRONOME_SOUND, interval = 1):
        pygame.mixer.init()
        self._metronome_sound=pygame.mixer.Sound(sound)
        self._metronome = sdutils.RepeatedTimer(interval, pygame.mixer.Sound.play, self._metronome_sound)

    def start(self):
        self._metronome.start()

    def stop(self):
        self._metronome.stop()
