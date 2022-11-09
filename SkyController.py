from led_controller import LEDController
from SkyGenerator import *
import time
import sys
import inspect
import copy
import threading

class SkyController:
    def __init__(self) -> None:
        w = 500
        h = 500
        x = 14
        y = 14

        self.sky = LEDController(x, y) 
        
        self.reset()
        ### Insert initial Generator here
        self.generator = DropGenerator(x, y, self.dt)
        ###

        self.running = False
        self.available_modes = self.get_available_classes()

    def get_available_classes(self):
        clsmembers = inspect.getmembers(sys.modules["SkyGenerator"], inspect.isclass)
        filtered_classes = list(filter(lambda cls: cls[0][-9::] == "Generator", clsmembers))
        information = {}
        for idx, item in enumerate(filtered_classes):
            dict = {}
            cls = item[1](14, 14, 1/60)
            name = cls.get_name()
            dict["name"] = name
            dict["id"] = idx
            dict["class"] = cls
            information[idx] = dict
        return information

    def get_available_modes(self):
        l = copy.deepcopy(list(self.available_modes.values()))
        for item in l:
            del item["class"]
        return l

    def reset(self):
        self.it = 0
        self.t = 0
        self.dt = 1/60

    def set_mode(self, id):
        self.reset()
        self.generator = self.available_modes[id]["class"]

    def set_color(self, color):
        self.generator.set_random_mode(False)
        self.generator.set_color(color)

    def set_random_mode(self, random):
        self.generator.set_random_mode(random)

    def set_speed(self, speed):
        self.generator.set_speed(speed)

    def set_brightness(self, brightness):
        self.generator.set_brightness(brightness)

    def start(self):
        self.running = True

    def stop(self):
        self.running = False
        self.sky.clear_leds()

    def main_loop(self):
        while (True):
            while self.running:
                arr = self.generator.generate(self.t, self.it)
                self.send_data(arr)
                time.sleep(self.dt)
                self.t += self.dt
                self.it += 1
            time.sleep(self.dt)

    def send_data(self, data):
        self.sky.set_lights(data)

if __name__ == "__main__":
    con = SkyController()
    threading.Thread(target=con.main_loop).start()
    con.start()
