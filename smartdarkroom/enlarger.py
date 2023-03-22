import time

class Enlarger():
    def __init__(self, light):
        self.light = light
        self.light.off()

    def focus_on(self):
        self.light.on()

    def focus_off(self):
        self.light.off()

    def print(self, seconds):
        self.light.on()
        time.sleep(seconds)
        self.light.off()
