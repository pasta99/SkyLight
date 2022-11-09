class LightSpec:

    def __init__(self, ca) -> None:
        self.r, self.g, self.b, self.a = ca
        
    def set_color(self, color):
        self.r, self.g, self.b, self.a = color

    def set_color_ci(self, color, intensity):
        self.r, self.g, self.b = color
        self.a = intensity

    def to_string(self):
        return "({},{},{},{})".format(self.r, self.g, self.b, self.a)