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

    def print(self, seconds, before_print_seconds, before_print_light):
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
            print(f"Step {i}: {step!r}")
            print(step.user_prompt)
            input("Press the ENTER key to continue...")
            self.print(step.duration, step.before_step_duration, step.before_step_light)

    def _preview_print(self, the_print):
        print("*** PRINT STRATEGY PREVIEW ***")
        print(the_print)
        print("*** END PRINT STRATEGY PREVIEW ***")
        print("")

class Metronome():
    def __init__(self, sound = METRONOME_SOUND, interval = 1):
        pygame.mixer.init()
        self._metronome_sound=pygame.mixer.Sound(sound)
        self._metronome = sdutils.RepeatedTimer(interval, pygame.mixer.Sound.play, self._metronome_sound)

    def start(self):
        self._metronome.start()

    def stop(self):
        self._metronome.stop()

def _play_after_preview_sound(sound = AFTER_PREVIEW_SOUND, repeat=2):
    pygame.mixer.init()
    after_preview_sound = pygame.mixer.Sound(sound)
    for _ in range(repeat):
        pygame.mixer.Sound.play(after_preview_sound)