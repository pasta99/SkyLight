import board
import neopixel
from time import sleep

pixels = neopixel.NeoPixel(board.D18, 200, brightness = 1)
pixels.fill((0, 0, 0))
pixels.show()
