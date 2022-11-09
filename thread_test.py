import time
import threading
from SkyController import SkyController

def basic():
    i = 0
    while i < 10:
        print(i)
        i+=1
        time.sleep(1)

print("Started")
threading.Thread(target=SkyController().start).start()
print("YAY")
input("Say smth")