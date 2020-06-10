from Point import Point
from Height_Map import Height_Map
import noise

class Beach_Agent:
    def __init__(self, tokens, beach_noise_max, octave):
        self.tokens = tokens
        self.beach_list = None
        self.beach_noise_max = beach_noise_max
        self.octave = octave
    
    def generate(self, height_map):
        self.define_shoreline(height_map)
        self.beach_list = height_map.get_points_of_type('shore')
        for point in self.beach_list:
            if noise.pnoise2(point.getX() / 10, point.getY() / 10, 1, .5, 2) > .5:
                point.set_biome('coast')
        while self.tokens > 0:
            self.beachify(self.beach_list, height_map)
            self.tokens -= 1
            self.beach_list = self.beach_list
    
    def beachify(self, beach_list, height_map):
        while len(beach_list) > 0:
            beach_point = beach_list.pop()
            point = height_map.get_random_neighbor_of_type(beach_point, 'coast')
            if point != None and self.tokens > 1 and ((noise.pnoise2(point.getX() / self.octave, point.getY() / self.octave) + 1) / 2) < self.beach_noise_max:
                point.set_biome('beach')
            if beach_point.get_elevation() > 1:
                beach_point.set_elevation(beach_point.get_elevation() - 1)
    
    def define_shoreline(self, height_map):
        coast_points = height_map.get_points_of_type('coast')
        for point in coast_points:
            if len(height_map.get_neighbors_of_type(point, 'ocean')) > 0:
                if noise.pnoise2(point.getX() / self.octave, point.getY() / self.octave) < self.beach_noise_max:
                    point.set_biome('shore')
                else:
                    point.set_biome('tallShore')
    