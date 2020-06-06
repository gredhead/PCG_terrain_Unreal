from Point import Point
import random

class Height_Map:
    def __init__(self, width, height, random_seed):
        self.width = width
        self.height = height
        self.random_seed = random_seed
        random.seed(random_seed)
        self.height_map = []
        ypos = -1
        for i in range(0, width * height):
            xpos = i % width
            if xpos == 0:
                ypos += 1
            self.height_map.append(Point(0, 'ocean', xpos, ypos))
            
    def point(self, x, y):
        if x < 0 or x > self.width - 1 or y < 0 or y > self.height - 1:
            print("Map Error: Attempted to access non existant point")
            return None
        return self.height_map[y * self.width + x]
    
    def get_neighbor(self, point, direction):
        on_left = False
        on_right = False
        on_top = False
        on_bottom = False
        x = point.getX()
        y = point.getY()
        if x == 0:
            on_left == True
        if x == self.width - 1:
            on_right = True
        if y == 0:
            on_top = True
        if y == self.height - 1:
            on_bottom = True
        if direction == 'west' and not on_left:
            return self.point(x - 1, y)
        if direction == 'north' and not on_top:
            return self.point(x, y - 1)
        if direction == 'east' and not on_right:
            return self.point(x + 1, y)
        if direction == 'south' and not on_bottom:
            return self.point(x, y + 1)
        if direction == 'northwest' and not on_left and not on_top:
            return self.point(x - 1, y - 1)
        if direction == 'northeast' and not on_right and not on_top:
            return self.point(x + 1, y - 1)
        if direction == 'southeast' and not on_right and not on_bottom:
            return self.point(x + 1, y + 1)
        if direction == 'southwest' and not on_left and not on_bottom:
            return self.point(x - 1, y + 1)
        
        return None
    
    def get_neighbors(self, point, only_orthogonal = False):
        neighbors = [self.get_neighbor(point, 'west'),
                     self.get_neighbor(point, 'northwest'),
                     self.get_neighbor(point, 'north'),
                     self.get_neighbor(point, 'northeast'),
                     self.get_neighbor(point, 'east'),
                     self.get_neighbor(point, 'southeast'),
                     self.get_neighbor(point, 'south'),
                     self.get_neighbor(point, 'southwest')]
        result = []
        for i in range(0, len(neighbors)):
            if only_orthogonal and i % 2 == 1:
                continue
            if neighbors[i] != None:
                result.append(neighbors[i])
        return result
    
    def get_random_neighbor(self, point, only_orthogonal = False):
        neighbors = self.get_neighbors(point, only_orthogonal)
        return random.choice(neighbors)
    
    def get_random_neighbor_of_type(self, point, biome, only_orthogonal = False):
        if len(self.get_neighbors_of_type(point, biome, only_orthogonal)) == 0:
            return None
        return random.choice(self.get_neighbors_of_type(point, biome, only_orthogonal))
    
    def has_neighbors(self, point, only_orthogonal = False):
        neighbors = self.get_neighbors(point, only_orthogonal)
        return len(neighbors) > 0
    
    def has_neighbors_of_type(self, point, biome, only_orthogonal = False):
        neighbors = self.get_neighbors_of_type(point, biome, only_orthogonal)
        return len(neighbors) > 0
    
    def get_neighbors_of_type(self, point, biome, only_orthogonal = False):
        neighbors = self.get_neighbors(point, only_orthogonal)
        result = []
        for i in range(0, len(neighbors)):
            if neighbors[i].get_biome() == biome:
                result.append(neighbors[i])
        return result
    
    def get_points_of_type(self, biome):
        result = []
        for i in range(0, len(self.height_map)):
            if self.height_map[i].get_biome() == biome:
                result.append(self.height_map[i])
        return result
    
    def get_random_point_of_type(self, biome):
        points = self.get_points_of_type(biome)
        if len(points) > 0:
            return random.choice(points)
        return None
    
    def random_direction(self):
        return random.choice(['west', 'northwest', 'north', 'northeast', 'east', 'southeast', 'south', 'southwest'])
    
    def get_map(self):
        return self.height_map
