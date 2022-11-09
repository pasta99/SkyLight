import board
import neopixel
from time import sleep
from LightSpec import LightSpec

class LEDController:

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.pixels = neopixel.NeoPixel(board.D18, w * h, brightness = 1, auto_write=False)

    def maximise_color(self, color):
        max_value = max(color)
        if max_value == 0:
            return (0,0,0)
        factor = 255 / max_value
        return tuple(int(factor * x) for x in color)

    def format_color(self, color):
        color_f = (color.g, color.r, color.b)
        color_f = self.maximise_color(color_f)
        return tuple(int(color.a * x) for x in color_f)

    def set_lights(self, leds):
        led_format = []
        for i in range(len(leds)):
            if i % 2 == 0:
                led_format.append(leds[i])
            else:
                led_format.append(reversed(leds[i]))
        led_final = []
        for i in range(len(led_format)):
            for item in led_format[i]:
                led_final.append(self.format_color(item))
        for i in range(len(led_final)):
            self.pixels[i] =led_final[i]
        self.pixels.show()

    def clear_leds(self):
        self.pixels.fill((0,0,0))
        self.pixels.show()

    def test_leds(self):
        while(True):
            for x_i in range(self.w):
                for y_i in range(self.h):
                    arr = []
                    for x in range(self.w):
                        subarr = []
                        for y in range(self.h):
                            if x == x_i and y == y_i:
                                subarr.append(LightSpec((255, 255, 255, 1)))
                            else:
                                subarr.append(LightSpec((0, 0, 0, 0)))
                        arr.append(subarr)
                    self.set_lights(arr)
                    sleep(0.1)

if __name__ == "main":
    try:
        leds = LEDController(7, 7)
        leds.test_leds()
    except:
        leds.clear_leds()