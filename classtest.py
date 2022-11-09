import sys
import inspect
from SkyGenerator import PerlinGenerator
clsmembers = inspect.getmembers(sys.modules["SkyGenerator"], inspect.isclass)
print(len(clsmembers))
print(clsmembers[0][0][-9::] == "Generator")
filtered_classes = list(filter(lambda cls: cls[0][-9::] == "Generator", clsmembers))
print(filtered_classes)
print(filtered_classes[0][1](14, 14).get_name())

information = {}
for idx, item in enumerate(filtered_classes):
    dict = {}
    cls = item[1](14, 14)
    name = cls.get_name()
    dict["name"] = name
    dict["id"] = idx
    dict["class"] = cls
    information[idx] = dict

print(information)