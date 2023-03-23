import time
import os
import smartdarkroom.utils as sdutils
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

METRONOME_SOUND = os.getenv('METRONOME_SOUND', 'smartdarkroom/resources/metronome_click.wav')


class Enlarger():
    def __init__(self, light):
        self.light = light
        self.light.off()

    def focus_on(self):
        self.light.on()

    def focus_off(self):
        self.light.off()

    def print(self, seconds):
        metronome = Metronome()
        self.light.on()
        time.sleep(seconds)
        self.light.off()
        metronome.stop()


class Metronome():
    def __init__(self, sound = METRONOME_SOUND, interval = 1):
        pygame.mixer.init()
        self._metronome_sound=pygame.mixer.Sound(sound)
        self._metronome = sdutils.RepeatedTimer(interval, pygame.mixer.Sound.play, self._metronome_sound)

    def start(self):
        self._metronome.start()

    def stop(self):
        self._metronome.stop()
