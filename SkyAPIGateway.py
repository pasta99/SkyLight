from SkyController import SkyController
import time
from flask import Flask
import threading
import json 

app = Flask(__name__)
controller = SkyController()
try:
    threading.Thread(target=controller.main_loop).start()
    time.sleep(1)
    controller.start()
except Exception as e:
    print(e) 
finally:
    controller.stop()

class SkyAPIGateway:
    def __init__(self, controller):
        self.controller = controller
        self.a = 1
        print("OK")

    def start(self):
        time.sleep(5)
        self.controller.reset()

    @app.route("/start/")
    def start():
        controller.start()
        return "True"

    @app.route("/stop/")
    def stop():
        controller.stop()
        return "True"

    @app.route("/modes/")
    def modes():
        modes = controller.get_available_modes()
        return json.dumps(modes)

    @app.route("/set/<id>/")
    def set_modes(id):
        controller.set_mode(int(id))
        return "Yes"

    @app.route("/color/<int:r>/<int:g>/<int:b>/")
    def set_color(r, g, b):
        controller.set_color((r, g, b))
        return "True"

    @app.route("/color/random/")
    def random_mode():
        controller.set_random_mode(True)
        return "True"

    @app.route("/speed/<float:speed>/")
    def set_speed(speed):
        controller.set_speed(speed)
        return "True"

    @app.route("/brightness/<float:brightness>/")
    def set_brightness(brightness):
        controller.set_brightness(brightness)
        return "True"