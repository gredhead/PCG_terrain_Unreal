from Point import Point
from Height_Map import Height_Map
from Coast_Agent import Coast_Agent
from Beach_Agent import Beach_Agent
from Mountain_Agent import Mountain_Agent
import math
from PIL import Image
import png
import numpy as np

# Map_Generator(1024, 1024, 1, 17, 4, 3, 5, 2, 15, 10, 240, 50, 50)

class Map_Generator:
    def __init__(self, width, height, seed, coast_size, coast_smoothness, inland, beach_height, coast_uniformity, num_mountains, mountain_width, mountain_max_height, squiggliness, mountain_smoothness):
        self.width = width
        self.height = height
        # 0 <= size <= ceiling(lg(mWidth * mHeight))
        # Below ceiling(lg(mWidth * mHeight))/2 is very small
        # Approaching the ceiling (ceiling(lg(mWidth * mHeight)) and ceiling(lg(mWidth * mHeight))-1
        # results in the same island with two agents) too closely leads to suicides and no growth if few enough agents
        self.coast_size = coast_size
        # 0 <= smoothness < size
        # 7-9 is when the star pattern usually starts developing (should probably stick below 7 or 8)
        self.coast_smoothness = coast_smoothness
        # Controls how far inland the coastline will go
        # 1 <= inland <= 3
        self.inland = inland
        # Controls how high beaches can reach
        # 0 <= beachHeight <= 10
        self.beach_height = beach_height
        # Controls how uniform the coastline is (i.e. is it one connected beach or many disconnected beaches?)
        #0 <= coastUniformity <= 3
        self.coast_uniformity = coast_uniformity
        # Set number of mountain ranges
        # 0 <= numMountainRanges <= 10
        self.num_mountains = num_mountains
        # islandCircumference / 10 <= widthMountainRange <= islandCircumference / 3
        self.mountain_width = mountain_width
        # 150 <= maxHeightMountainRange <= 250
        self.mountain_max_height = mountain_max_height
        # 1 <= squiggliness <= 90
        # Equal to minturnangle, maxturnangle = 2*squiggliness
        self.squiggliness = squiggliness
        # Controls how quickly mountains drop to the ground
        #0 <= smoothness <= 100
        self.mountain_smoothness = mountain_smoothness
        
    
    def set_width(self, new_width):
        self.width = new_width
    
    def set_height(self, new_height):
        self.height = new_height
    
    def set_coast_size(self, amount):
        self.coast_size = amount
    
    def set_coast_smoothness(self, amount):
        self.coast_smoothness = amount
    
    def set_inalnd(self, amount):
        self.inland = amount
    
    def set_beach_height(self, amount):
        self.beach_height = amount
    
    def set_coast_uniformity(self, amount):
        self.coast_uniformity = amount
    
    def set_num_mountains(self, amount):
        self.num_mountains = amount
    
    def set_mountain_width(self, amount):
        self.mountain_width = amount
        
    def set_mountain_max_height(self, amount):
        self.mountain_max_height = amount
        
    def set_squiggliness(self, amount):
        self.squiggliness = amount
        
    def set_mountain_smoothness(self, amount):
        self.mountain_smoothness = amount
    
    def create_height_map(self):
        island_area = math.pow(2, self.coast_size)
        # island_circumference = 2 * math.pi * math.sqrt(island_area / math.pi)
        coast_agents = math.pow(2, self.coast_smoothness)
        coast_tokens = island_area
        coast_limit = coast_tokens / coast_agents
        coast_octave = math.pow(10, self.coast_uniformity)
        
        mountain_tokens = math.ceil(island_area / self.mountain_width * .3)
        mountain_max_peak = self.mountain_max_height
        mountain_min_peak = mountain_max_peak
        mountain_max_walk_time = math.ceil((1 - (self.squiggliness / 100)) * mountain_tokens * .05)
        mountain_min_walk_time = math.ceil(mountain_max_walk_time / 2)
        mountain_min_turn = self.squiggliness
        mountain_max_turn = self.squiggliness * 2
        
        height_map = Height_Map(self.width, self.height, 5)
        coast_start = height_map.point(math.floor(self.width / 2), math.floor(self.height / 2))
        coast = Coast_Agent(coast_start, coast_tokens, coast_limit)
        beach = Beach_Agent(self.inland, self.beach_height / 10, coast_octave)
        mountain = Mountain_Agent(self.num_mountains, mountain_tokens, self.mountain_width, mountain_min_peak, mountain_max_peak, mountain_min_walk_time, mountain_max_walk_time, mountain_min_turn, mountain_max_turn, self.mountain_smoothness, 1, 1)
        
        coast.generate(height_map)
        beach.generate(height_map)
        mountain.generate(height_map)
        
        for i in height_map.get_map():
            i.set_elevation(i.get_elevation() / 5)
        
        for beach in height_map.get_points_of_type('beach'):
            self.smooth_area(height_map, 3, beach.getX(), beach.getY())
        for beach in height_map.get_points_of_type('beach'):
            self.smooth_area(height_map, 4, beach.getX(), beach.getY())
        
        return height_map.get_map()
    
    def smooth_point(self, height_map, x, y):
        total = height_map.point(x, y).get_elevation() * 3
        if height_map.point(x-1, y) != None:
            total += height_map.point(x-1, y).get_elevation()
        if height_map.point(x-2, y) != None:
            total += height_map.point(x-2, y).get_elevation()
        if height_map.point(x+1, y) != None:
            total += height_map.point(x+1, y).get_elevation()
        if height_map.point(x+2, y) != None:
            total += height_map.point(x+2, y).get_elevation()
        if height_map.point(x, y-1) != None:
            total += height_map.point(x, y-1).get_elevation()
        if height_map.point(x, y-2) != None:
            total += height_map.point(x, y-2).get_elevation()
        if height_map.point(x, y+1) != None:
            total += height_map.point(x, y+1).get_elevation()
        if height_map.point(x, y+2) != None:
            total += height_map.point(x, y+2).get_elevation()
        total /= 11
        height_map.point(x, y).set_elevation(total)
    
    def smooth_area(self, height_map, width, x, y):
        for i in range(x - width, x + width):
            for j in range(y - width, y + width):
                if x < 0 or y < 0 or x > self.width - 1 or y > self.height - 1:
                    continue
                if height_map.point(x, y).dist(height_map.point(i, j)) <= width:
                    self.smooth_point(height_map, i, j)

        
    
blah = Map_Generator(1024, 1024, 1, 17, 4, 3, 5, 2, 5, 30, 30, 30, 100)
point_map = blah.create_height_map()
real_map2 = []
for i in point_map:
    real_map2.append(i.get_elevation())
    


point_map[0].set_elevation(50)

real_map = []
for i in point_map:
    real_map.append((i.get_elevation(), 0, 0))
real_map = np.reshape(real_map, (1024, 1024, 3))

map_z = (65535*((real_map - real_map.min())/real_map.ptp())).astype(np.uint16)
map_grey = map_z[:, :, 0]

with open('map1.png', 'wb') as f:
    writer = png.Writer(width = map_z.shape[1], height = map_z.shape[0], bitdepth = 16, greyscale = True)
    map_list = map_grey.tolist()
    writer.write(f, map_list)






for i in range(blah.width):
    for j in range(blah.height):
        blah.smooth_point(point_map, i, j)

img = Image.fromarray(real_map2)
img.show()


real_map2 = [i.astype(np.uint8) for i in real_map2]
real_map2 = np.reshape(real_map2, (1024, 1024))