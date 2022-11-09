import board
import neopixel
from time import sleep
import random
import math

pixels = neopixel.NeoPixel(board.D18, 200, brightness = .1, auto_write=False)

it = 0
while True:
	color = (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255))
	color = (0, int((math.sin(it * 0.05) + 1) * 255 / 2), 0)
	for i in range(200):
		if it == 0:
			pixels[i] = color
		else: 
			pixels[i] = color
	pixels.show()
	it += 1
	sleep(1/120)
