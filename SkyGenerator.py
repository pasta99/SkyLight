
from LightSpec import LightSpec
import math
import numpy as np
from perlin_noise import PerlinNoise
import random

class SkyGenerator:
    name = 'default'
    min_speed = 5
    max_speed = 15
    speed = 1
    color = (0, 0, 255)
    random_mode = False
    brightness = 1

    def __init__(self, x, y, dt) -> None:
        self.x = x
        self.y = y
        self.dt = dt

    def get_name(self):
        return self.name

    def set_speed(self, speed):
        self.speed = self.clip_intensity(speed)
    
    def set_color(self, color):
        self.color = color

    def set_brightness(self, brightness):
        self.brightness = brightness

    def adjust_grid_for_brightness(self, grid):
        for x in range(len(grid)):
            for y in range(len(grid[0])):
                grid[x][y].a *= self.brightness
        return grid

    def set_random_mode(self, random):
        self.random_mode = random

    def get_random_color(self):
        return tuple(np.random.choice(range(256), size=3))

    def set_random_color(self):
        if (self.random_mode):
            self.color = self.get_random_color()

    def get_speed(self):
        return self.min_speed + self.speed * (self.max_speed - self.min_speed)

    def clip_intensity(self, x):
        return max(0, min(1, x))

    def get_id_of_led(self, x, y):
        return x + y * self.x

    def cart2pol(self, x, y):
        rho = np.sqrt(x**2 + y**2)
        phi = np.arctan2(y, x)
        return(rho, phi)

    def pol2cart(self, rho, phi):
        x = rho * np.cos(phi)
        y = rho * np.sin(phi)
        return(x, y)

    def normalize(self, x, y):
        x_n = (x - (self.x / 2)) / self.x
        y_n = (y - (self.y / 2)) / self.y
        return (x_n, y_n)

    def spike_sin(self, t):
        t_n = t % 2
        if t_n < 1:
            return t_n
        else: 
            return 2 - t_n

    def spike_sin_d(self, t):
        t_n = t % 2
        if t_n < 1:
            return 1
        else: 
            return -1

    def normalized_sin(self, t):
        return 0.5 * (math.sin(t) + 1)
    
    def saw(self, t):
        return t % 1 

    def rotate_point(self, x, y, angle):
        s = math.sin(angle)
        c = math.cos(angle)
        return (x * c - y * s, x * s + y * c)

    def linear_interpolation(self, x0, x1, y0, y1, x):
        return y0 + (x - x0) * (y1 - y0) / (x1 - x0)

    def random_color(self):
        return list(np.random.choice(range(256), size=3))

    def length(self, x, y):
        return math.sqrt(x**2 + y**2)

    def generate(self, t, it):
        grid = self.get_blank_grid()
        grid = self.generate_image(t, it, grid)
        grid = self.adjust_grid_for_brightness(grid)
        return grid

    def generate_image(self, t, it, grid):
        for x in range(self.x):
            for y in range(self.y):
                if (x + y) % 2 == (it % 2):
                    grid[x][y].set_color((255, 0, 0, 1))
                else:
                    grid[x][y].set_color((0, 255, 0, 1))
        return grid

    def get_blank_grid(self):
        arr = []
        for x in range(self.x):
            subarr = []
            for y in range(self.y):
                subarr.append(LightSpec((0, 0, 0, 0)))
            arr.append(subarr)
        return arr
            
class MonotoneBlinkGenerator(SkyGenerator):
    name = "Monotone Blinking"
    min_speed = 1
    max_speed = 15

    def generate_image(self, t, it, grid):       
        # When lights out change color when random mode
        if math.sin(t * self.get_speed()) < -0.99:
            self.set_random_color()

        for x in range(self.x):
            for y in range(self.y):
                grid[x][y].set_color_ci(self.color, self.clip_intensity(math.sin(t * self.get_speed()) * 0.5 + 0.5))
        return grid

class LinearGenerator(SkyGenerator):
    name = "Linear"
    min_speed = 0.1
    max_speed = 2
    leadpoint = 0

    def generate_image(self, t, it, grid):
        # set random color after a whole iteration
        if ((it % (2 * self.x * self.y)) == 0):
            self.set_random_color()

        self.leadpoint += self.get_speed()
        self.leadpoint %= (2 * self.x * self.y)
    
        for x in range(self.x):
            for y in range(self.y):
                id = self.get_id_of_led(x, y)
                intensity = 1 if self.leadpoint - id > 0 and self.leadpoint - id < (self.x * self.y) else 0
                grid[x][y].set_color_ci(self.color, intensity)
        return grid

class LineGenerator(SkyGenerator):
    name = "Line"
    min_speed = 0.1
    max_speed = 2
    leadpoint = 0

    def generate_image(self, t, it, grid):
        # set random color after a whole iteration
        if (self.leadpoint == 0):
            self.set_random_color()

        self.leadpoint += self.get_speed()
        self.leadpoint %= (self.x * self.y)

        for x in range(self.x):
            for y in range(self.y):
                id = self.get_id_of_led(x, y)
                # A line of 5 pixels is activated
                intensity = 1 if self.leadpoint - id > 0 and self.leadpoint - id < 5 else 0
                grid[x][y].set_color_ci(self.color, intensity)
        return grid

class MultiColorLineGenerator(SkyGenerator):
    name = "Colorful Line"
    min_speed = 0.1
    max_speed = 2
    leadpoint = 0

    def generate_image(self, t, it, grid):
        total = self.x * self.y
        colors = [[255, 0, 0, 1], [255, 165, 0, 1], [255, 255, 0, 1], [0, 255, 0, 1], [0, 0, 255, 1], 
        [160,32,240, 1], [255, 0, 0, 1], [255, 165, 0, 1], [255, 255, 0, 1], [0, 255, 0, 1], [0, 0, 255, 1], [160,32,240, 1],
        [255, 0, 0, 1], [255, 165, 0, 1], [255, 255, 0, 1], [0, 255, 0, 1], [0, 0, 255, 1], [160,32,240, 1]]
        self.leadpoint += self.get_speed()
        self.leadpoint %= total
        for x in range(self.x):
            for y in range(self.y):
                num = x + y * self.x
                index = int((num + self.leadpoint) % total / math.ceil(total / len(colors)))
                grid[x][y].set_color(colors[index])
        return grid

class CircleGenerator(SkyGenerator):
    name = "Circle"
    min_speed = 0.25
    max_speed = 3
    radius = 0.15
    mode = 0

    def generate_image(self, t, it, grid):
        if self.mode == 0:
            self.radius += self.get_speed() *  self.dt
        else:
            self.radius -= self.get_speed() *  self.dt

        if self.radius > 0.5:
            self.mode = 1
        elif self.radius < 0.15:
            self.mode = 0
            self.set_random_color()
        
        for x in range(self.x):
            for y in range(self.y):
                x_n, y_n = self.normalize(x, y)
                magnitude = self.length(x_n, y_n)
                intensity = np.interp(magnitude, [0, 0.85 * self.radius, self.radius], [1, 1, 0])
                grid[x][y].set_color_ci(self.color,intensity)
        return grid

class LinearInterpGenerator(SkyGenerator):
    def get_name(self):
        return "Linear interpolation"
    def generate_image(self, t, it):
        arr = []
        max_p = self.spike_sin(t * 10) * 0.8
        for x in range(self.x):
            subarr = []
            for y in range(self.y):
                x_n, y_n = self.normalize(x, y)
                magnitude = self.length(x_n, y_n)
                intensity = np.interp(magnitude, [0, max_p, 0.8], [0, 1, 0])
                intensity = np.interp(magnitude, [max_p - 0.1, max_p, max_p + 0.1], [0, 1, 0])
                subarr.append(LightSpec((255, 255, 0, intensity)))
            arr.append(subarr)
        return arr

class DropGenerator(SkyGenerator):
    name = "Rain"
    thickness = 0.2
    points = []
    speed = []
    times = []
    next_drop_time = 0

    def generate_image(self, t, it):
        arr = []
        max_p = self.spike_sin(t * 10) * 0.8
        if it == self.next_drop_time:
            self.points.append([random.random() - 0.5, random.random() - 0.5])
            self.speed.append(3)
            self.times.append(t)
            self.next_drop_time += np.random.choice(range(20, 40))
        for x in range(self.x):
            subarr = []
            for y in range(self.y):
                x_n, y_n = self.normalize(x, y)
                intensity = 0
                delete_list = []
                for i in range(len(self.points)):
                    magnitude_to_point = self.length(x_n - self.points[i][0], y_n - self.points[i][1])
                    radius = (t - self.times[i]) * self.speed[i]
                    if radius > 2:
                        delete_list.append(i)
                    intensity += np.interp(magnitude_to_point, [radius - self.thickness / 2, radius, radius + self.thickness / 2], [0, 1, 0])
                intensity = min(1, intensity)
                subarr.append(LightSpec((0, 0, 255, intensity)))
                for i in range(len(delete_list)):
                    del self.points[i]
                    del self.speed[i]
                    del self.times[i]
            arr.append(subarr)
        return arr

class ColorPulseGenerator(SkyGenerator):
    name = "Colorful pulse"
    thickness = 0.2
    points = []
    speed = []
    times = []
    next_drop_time = 0
    colors = [[255, 0, 0], [0, 0, 255], [0, 255, 0]]
    colorindex = []

    def generate_image(self, t, it):
        arr = []
        max_p = self.spike_sin(t * 10) * 0.8
        if it == self.next_drop_time:
            self.points.append([0,0])
            self.speed.append(3)
            self.times.append(t)
            self.next_drop_time += 5
            self.colorindex.append(np.random.choice(range(0,len(self.colors)), size=1)[0])
        for x in range(self.x):
            subarr = []
            for y in range(self.y):
                x_n, y_n = self.normalize(x, y)
                intensity = 0
                delete_list = []
                color = [0,0,0]
                for i in range(len(self.points)):
                    magnitude_to_point = self.length(x_n - self.points[i][0], y_n - self.points[i][1])
                    radius = (t - self.times[i]) * self.speed[i]
                    if radius > 2:
                        delete_list.append(i)
                    intensity += np.interp(magnitude_to_point, [radius - self.thickness / 2, radius, radius + self.thickness / 2], [0, 1, 0])
                    color += self.colors[self.colorindex[0]]
                    # TODO: FIX
                intensity = min(1, intensity)
                color.append(intensity)
                subarr.append(LightSpec(color))
                for i in range(len(delete_list)):
                    del self.points[i]
                    del self.speed[i]
                    del self.times[i]
                    del self.colorindex[i]
            arr.append(subarr)
        return arr

class SquareGenerator(SkyGenerator):
    def get_name(self):
        return "Square"
    def generate_image(self, t, it):
        arr = []
        num_it = it % (self.x * self.y) 
        total = self.x * self.y
        for x in range(self.x):
            subarr = []
            for y in range(self.y):
                x_n, y_n = self.normalize(x, y)
                magnitude = self.length(x_n, y_n)
                intensity = 1 if max(x_n**2, y_n**2) < (t) % .4 else 0
                subarr.append(LightSpec((255, 255, 0, intensity)))
            arr.append(subarr)
        return arr

class BandGenerator(SkyGenerator):
    def get_name(self):
        return "Band"
    def generate_image(self, t, it):
        arr = []
        num_it = it % (self.x * self.y) 
        total = self.x * self.y
        for x in range(self.x):
            subarr = []
            for y in range(self.y):
                x_n, y_n = self.normalize(x, y)
                intensity = 0 if self.length(x_n, y_n) < (t * 4) % 1 and self.length(x_n, y_n) > (t * 4 - 0.2) % 1 else 1
                intensity = math.cos(self.length(x_n, y_n) * t * 10)
                color = list(np.random.choice(range(256), size=3))
                color = [255, 255, 0]
                color.append(intensity)
                subarr.append(LightSpec(color))
            arr.append(subarr)
        return arr

class CircularGenerator(SkyGenerator):
    def get_name(self):
        return "Circular"
    def generate_image(self, t, it):
        arr = []
        for x in range(self.x):
            subarr = []
            for y in range(self.y):
                x_n, y_n = self.normalize(x, y)
                rho, phi = self.cart2pol(x_n, y_n)
                intensity = 1 if phi < ((t * 10) % (2 * math.pi) - math.pi) else 0
                print((t * 10) % (2 * math.pi) - math.pi)
                if int(((t * 10) / (2 * math.pi)) - math.pi) % 2 == 1:
                    intensity = 1 - intensity
                subarr.append(LightSpec((255, 255, 0, intensity)))

            arr.append(subarr)
        return arr

class WaveGenerator(SkyGenerator):
    def get_name(self):
        return "Waves"
    def generate_image(self, t, it):
        arr = []
        num_it = it % (self.x * self.y) 
        total = self.x * self.y
        for x in range(self.x):
            subarr = []
            for y in range(self.y):
                x_n, y_n = self.normalize(x, y)
                intensity = math.sin(t * x ) * 0.5 + 0.5
                subarr.append(LightSpec((255, 255, 0, intensity)))
            arr.append(subarr)
        return arr

class PerlinGenerator(SkyGenerator):
    def get_name(self):
        return "Sponsored by Perlin"
    def __init__(self, x, y, dt) -> None:
        self.x = x
        self.y = y
        self.noise = PerlinNoise(octaves=3.5)
        self.dt = dt

    def generate_image(self, t, it):
        arr = []       
        for x in range(self.x):
            subarr = []
            for y in range(self.y):
                x_n, y_n = self.normalize(x, y)
                intensity = self.clip_intensity(self.noise([(x * t * 0.1),(y * t * 0.1)]))
                subarr.append(LightSpec((255, 255, 0, intensity)))
            arr.append(subarr)
        return arr

class StarGenerator(SkyGenerator):
    def get_name(self):
        return "Starry sky"
    def __init__(self, x, y, dt) -> None:
        self.x = x
        self.y = y
        self.dt = dt
        self.noise = PerlinNoise(octaves=3.5)
        self.noise = np.random.normal(0.5, 0.2, size=(x, y))

    def generate_image(self, t, it):
        arr = []       
        for x in range(self.x):
            subarr = []
            for y in range(self.y):
                x_n, y_n = self.normalize(x, y)
                intensity = math.sin(max(self.noise[x,y], 0.01) * 7 * t) * 0.5 + 0.5
                subarr.append(LightSpec((255, 255, 0, self.clip_intensity(intensity))))
            arr.append(subarr)
        return arr

class HeartGenerator(SkyGenerator):
    def get_name(self):
        return "ILuvYu"
    def generate_image(self, t, it):
        arr = []
        for x in range(self.x):
            subarr = []
            for y in range(self.y):
                x_n, y_n = self.normalize(x, y)
                y_n *= -1 
                y_n += 0.1
                intensity = 1 if (x_n ** 2 + y_n ** 2 - 0.05 * (math.sin(t * 10) + 1)) ** 3 < x_n ** 2 * y_n ** 3 else 0
                dist = (x_n ** 2 + y_n ** 2 - 0.05 * (math.sin(t * 10) + 1)) ** 3 - x_n ** 2 * y_n ** 3
                intensity = 1 if dist < 0 else 0             
                if dist < 0.001 and dist > 0:
                    pass
                    #intensity = np.interp(dist, [0, 0.001], [1, 0])
                color = [255, 0, 0]
                color.append(intensity)
                subarr.append(LightSpec(color))
            arr.append(subarr)
        return arr

class MetronomeGenerator(SkyGenerator):
    def get_name(self):
        return "Metronome"
    def generate_image(self, t, it):
        arr = []
        for x in range(self.x):
            subarr = []
            for y in range(self.y):
                x_n, y_n = self.normalize(x, y)
                rho, phi = self.cart2pol(x_n, y_n)
                intensity = 1 
                if phi < math.sin(t * 10) * math.pi:
                    color = [255, 0, 0]
                else:
                    color = [0, 255, 0]
                color.append(intensity)
                subarr.append(LightSpec(color))

            arr.append(subarr)
        return arr

class DiskGenerator(SkyGenerator):
    def get_name(self):
        return "Spinning"
    def generate_image(self, t, it):
        arr = []
        for x in range(self.x):
            subarr = []
            for y in range(self.y):
                x_n, y_n = self.normalize(x, y)
                rho, phi = self.cart2pol(x_n, y_n)
                intensity = 1 
                phi_n = (phi + math.pi) / (2 * math.pi)
                t_p = t * 10
                t_n = math.sin(t_p) * 0.5 + 0.5
                t_n = (t * 4) % 1 
                diff = abs(phi_n - t_n)
                if diff < 0.75 and diff > 0.25: 
                    color = [255, 0, 0]
                else:
                    color = [0, 255, 0]
                color.append(intensity)
                subarr.append(LightSpec(color))

            arr.append(subarr)
        return arr

class LightHouseGenerator(SkyGenerator):
    def get_name(self):
        return "Lighthouse"
    def generate_image(self, t, it):
        arr = []
        for x in range(self.x):
            subarr = []
            for y in range(self.y):
                x_n, y_n = self.normalize(x, y)
                rho, phi = self.cart2pol(x_n, y_n)
                phi_n = (phi + math.pi) / (2 * math.pi)
                t_n = (t * 2) % 1 
                diff = abs(phi_n - t_n)
                if diff <= 0.66 and diff > 0.33:
                    color = [255, 255, 0]
                else: 
                    color = [0, 0, 0]
                co = 0.05
                intensity = np.interp(diff, [0.36 - co, 0.36, 0.63, 0.63 + co], [0, 1, 1, 0])
                color = [255, 255, 0]
                color.append(intensity)
                subarr.append(LightSpec(color))

            arr.append(subarr)
        return arr

class AngleLineGenerator(SkyGenerator):
    name = "Angled Lines"
    angle = 0
    last_t_n = 0
    length = 1.5
    co = 0.15

    def generate_image(self, t, it):
        arr = []
        t_n = (t * 3) % self.length - self.length / 2
        if (self.last_t_n - t_n) > 0.5:
            self.angle = random.random() * 2 * math.pi
        self.last_t_n = t_n
        
        for x in range(self.x):
            subarr = []
            for y in range(self.y):
                x_n, y_n = self.normalize(x, y)
                _, y_c = self.rotate_point(x_n, y_n, self.angle)             
                intensity = np.interp(y_c, [t_n - self.co, t_n, t_n + self.co], [0, 1, 0])
                color = [255, 255, 0]
                color.append(intensity)
                subarr.append(LightSpec(color))

            arr.append(subarr)
        return arr

class SpiralGenerator(SkyGenerator):
    def get_name(self):
        return "Spiral"
    def __init__(self, x, y, dt) -> None:
        self.x = x
        self.y = y
        self.radius = 0.15 
        self.angle = 0
        self.distance = 0
        self.speed_a = 0.5
        self.speed_d = 0.007  
        self.arr = []
        self.reset_arr()
        self.last_dist = 0

    def reset_arr(self):
        self.arr = []   
        for x in range(self.x):
            subarr = []
            for y in range(self.y):                
                subarr.append(0)
            self.arr.append(subarr)

    def generate_image(self, t, it):
        arr = []
        self.distance = (self.distance + self.speed_d) % 0.7
        self.angle = (self.angle + self.speed_a) % (2 * math.pi)
        x_p, y_p = self.pol2cart(self.distance, self.angle)
        for x in range(self.x):
            subarr = []
            for y in range(self.y):
                x_n, y_n = self.normalize(x, y)
                
                intensity = 0
                magnitude_to_point = self.length(x_n - x_p, y_n - y_p)
                
                self.arr[x][y] += np.interp(magnitude_to_point, [0, self.radius * 0.99, self.radius], [1, 1, 0])
                intensity = min(1, self.arr[x][y])
                subarr.append(LightSpec((255, 255, 0, intensity)))
            arr.append(subarr)
        if abs(self.last_dist - self.distance) > 0.5:
            self.reset_arr()
        self.last_dist = self.distance
        return arr

class DVDGenerator(SkyGenerator):
    def get_name(self):
        return "DVD"
    def __init__(self, x, y, dt) -> None:
        self.x = x
        self.y = y
        self.dt = dt
        self.direction = self.norm([random.random()+0.1, random.random() + 0.1])
        self.speed = 1
        self.pos = [0, 0]
        self.radius = 0.15

    def dot(self, x, y):
        return x[0] * y[0] + x[1] * y[1]

    def reflect(self, x, n):
        d = self.dot(x, n) 
        r = [0,0]
        r[0] = x[0] - (2 * d * n[0])
        r[1] = x[1] - (2 * d * n[1])
        return r

    def norm(self, x):
        l = self.length(x[0], x[1])
        return [x[0] / l, x[1] / l]

    def generate_image(self, t, it):
        arr = []
        self.pos[0] += self.speed * self.dt * self.direction[0]
        self.pos[1] += self.speed * self.dt * self.direction[1]
        if self.pos[0] > 0.5: 
            self.direction = self.reflect(self.direction, [-1, 0])
        elif self.pos[0] < -0.5:
            self.direction = self.reflect(self.direction, [1, 0])
        elif self.pos[1] > 0.5: 
            self.direction = self.reflect(self.direction, [0, -1])
        elif self.pos[1] < -0.5:
            self.direction = self.reflect(self.direction, [0, 1])
            self.pos[1] = -0.49

        for x in range(self.x):
            subarr = []
            for y in range(self.y):
                x_n, y_n = self.normalize(x, y)
                dist = self.length(self.pos[0] - x_n, self.pos[1] - y_n)          
                intensity = np.interp(dist, [0, self.radius * 0.95, self.radius], [1, 1, 0])
                color = [255, 255, 0]
                color.append(intensity)
                subarr.append(LightSpec(color))

            arr.append(subarr)
        return arr