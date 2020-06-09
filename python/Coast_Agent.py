from Height_Map import Height_Map
from Point import Point
import random
import math
import noise
import numpy as np

class Coast_Agent:
    def __init__(self, seed_point, tokens, limit):
        self.seed = seed_point
        self.tokens = tokens
        self.limit = limit
        self.direction = None
    
    def get_seed(self):
        return self.seed
    
    def set_seed(self, new_seed):
        self.seed = new_seed
    
    def get_tokens(self):
        return self.tokens
    
    def set_tokens(self, new_tokens):
        self.tokens = new_tokens
    
    def get_direction(self):
        return self.direction
    
    def set_direction(self, new_direction):
        self.direction = new_direction
    
    def random_direction(self, height_map):
        self.direction = height_map.random_direction()
    
    def generate(self, height_map):
        if self.direction == None:
            self.random_direction(height_map)
        self.recur_coast(height_map)
    
    def recur_coast(self, height_map):
        # print("recur coast at: " + str(self.seed))
        if self.tokens > self.limit:
            # print("splitting tokens: " + str(self.tokens))
            child1 = Coast_Agent(height_map.get_random_neighbor(self.seed), math.floor(self.tokens / 2), self.limit)
            child1.random_direction(height_map)
            child2 = Coast_Agent(height_map.get_random_neighbor(self.seed), math.floor(self.tokens / 2), self.limit)
            child2.random_direction(height_map)
            child1.recur_coast(height_map)
            child2.recur_coast(height_map)
        else:
            while self.tokens > 0:
                self.seed = height_map.get_random_neighbor(self.seed)
                self.move_agent(height_map)
                if self.seed == None:
                    break
                beacons = self.assign_beacons(self.seed, height_map)
                max_score = float("-inf")
                best_point = None
                for point in height_map.get_neighbors(self.seed):
                    point_score = self.score_point(point, beacons, height_map)
                    if point_score > max_score:
                        max_score = point_score
                        best_point = point
                self.random_direction(height_map)
                self.raise_point(best_point)
                self.tokens -= 1
    
    def raise_point(self, point):
        new_elevation = 0
        #print("add1: " + str(3 * (noise.pnoise2(point.getX() / 10, point.getY() / 10, 1, .5, 2) + 1)))
        new_elevation += (3 * (noise.pnoise2(point.getX() / 10, point.getY() / 10, 1, .5, 2) + 1))
        #print("add2: " + str(3 * (noise.pnoise2(point.getX() / 100, point.getY() / 100, 1, .5, 2) + 1)))
        new_elevation += (3 * (noise.pnoise2(point.getX() / 100, point.getY() / 100, 1, .5, 2) + 1))
        point.set_elevation(new_elevation)
        point.set_biome('coast')
        #print("raised: " + str(point))
        return point
    
    def assign_beacons(self, point, height_map):
        repulsor = height_map.get_random_neighbor(point)
        attractor = height_map.get_random_neighbor(point)
        while repulsor == attractor:
            repulsor = height_map.get_random_neighbor(point)
            attractor = height_map.get_random_neighbor(point)
        return [repulsor, attractor]
    
    def move_agent(self, height_map):
        while len(height_map.get_neighbors_of_type(self.seed, 'ocean')) == 0:
            self.seed = height_map.get_neighbor(self.seed, self.direction)
            if self.seed == None:
                return
    
    def score_point(self, point, beacons, height_map):
        if point.get_biome() != 'ocean':
            return float("-inf")
        repulsor = beacons[0]
        attractor = beacons[1]
        dist_repulsor = point.dist(repulsor)
        dist_attractor = point.dist(attractor)
        dist_center = min((height_map.width - 1 - point.getX()), (height_map.height - 1 - point.getY()), (point.getY()))
        return math.pow(dist_repulsor, 2) - math.pow(dist_attractor, 2) + 3 * math.pow(dist_center, 2)
            
random.random
