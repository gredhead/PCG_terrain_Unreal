from Point import Point
from Height_Map import Height_Map
import math
import random
import numpy as np

class Mountain_Agent:
    def __init__(self, number_of_mountains, tokens, width, height_min, height_max, turn_period_min, turn_period_max, turn_min, turn_max, dropoff, min_elevation, rand):
        self.x = 0;
        self.y = 0;
    
        self.number_of_mountains = number_of_mountains
        self.tokens = tokens
        self.direction = 0
        self.width = width
        self.height_min = height_min
        self.height_max = height_max
        self.turn_period_min = turn_period_min
        self.turn_period_max = turn_period_max
        self.turn_min = turn_min
        self.turn_max = turn_max
        self.dropoff = dropoff / 100 * 0.2 + 0.8
        self.min_elevation = min_elevation
        random.seed(rand)
    
    def pick_random_start(self, height_map):
        self.x = math.floor(random.randrange(0, height_map.width - 1))
        self.y = math.floor(random.randrange(0, height_map.height - 1))
        
    
    def check_point(self, height_map, x, y):
        if x < 0 or x > height_map.width - 1 or y < 0 or y > height_map.height - 1:
            #print("failed at point: " + str(x) + " " + str(y))
            return None
        else:
            return height_map.point(x, y)
    
    def check_start(self, height_map):
        for i in range(-self.width, self.width + 1):
            for j in range(-self.width, self.width + 1):
                if (
                    self.distance(round(self.x + i), round(self.y + j), round(self.x), round(self.y)) < self.width 
                    and self.check_point(height_map, round(self.x + i), round(self.y + j)) != None and height_map.point(round(self.x + i), round(self.y + j)).get_elevation() < self.min_elevation
                    ):
                    #print("bad starting area")
                    return True
        return False
    
    def reset_turn_timer(self):
        self.turn_time = random.randint(self.turn_period_min, self.turn_period_max)
    
    def generate(self, height_map):
        for mountain_count in range(0, self.number_of_mountains):
            self.pick_random_start(height_map)
            self.direction = random.randint(0, 360)
            count = 0
            while self.check_point(height_map, self.x, self.y) == None or height_map.point(self.x, self.y).get_elevation() < self.min_elevation or self.check_start(height_map):
                self.pick_random_start(height_map)
                count += 1
                if count > 1000:
                    #print("Max mountain attempts reached, aborting mountain range creation")
                    return
            reached_edge = False
            self.reset_turn_timer()
            time_since_turn = 0
            print("mountain start: " + str(self.x) + " " + str(self.y))
            for i in range(0, self.tokens):
                reached_edge = self.elevate_circle(height_map)
                if reached_edge == True:
                    self.turn_left(False)
                if self.turn_time > 0 and time_since_turn > self.turn_time:
                    self.make_foothills(height_map)
                    turn_amount = self.get_turn()
                    self.rotate_agent(turn_amount)
                    self.reset_turn_timer()
                    time_since_turn = 0
                self.move_agent()
                time_since_turn += 1
    
    def elevate_circle(self, height_map):
        #print("mountain: " + str(self.x) + ' ' + str(self.y))
        height = random.randint(self.height_min, self.height_max)
        reached_edge = False
        width = self.width + random.randint(-self.width / 5, self.width / 5)
        for i in range(-width, width + 1):
            for j in range(-width, width + 1):
                if self.distance(self.x + i, self.y + j, self.x, self.y) < width:
                    if reached_edge == False:
                        if self.set_height(height_map, math.floor(self.x + i), math.floor(self.y + j), self.height_with_dropoff(self.x, self.y, self.x + i, self.y + j, height)):
                            reached_edge = True
                    else:
                        self.set_height(height_map, math.floor(self.x + i), math.floor(self.y + j), self.height_with_dropoff(self.x, self.y, self.x + i, self.y + j, height))
        height_map.point(round(self.x), round(self.y)).set_biome('ridge')
        return reached_edge
    
    def elevate_foothill(self, height_map, x, y, height, width):
        reached_edge = False
        for i in np.arange(x - width, x + width + 1, 1):
            for j in np.arange(y - width, y + width + 1, 1):
                if self.distance(i, j, x, y) < width:
                    if reached_edge == False:
                        if self.set_height(height_map, math.floor(i), math.floor(j), self.height_with_dropoff(x, y, i, j, height)):
                            reached_edge = True
                    else:
                        self.set_height(height_map, math.floor(i), math.floor(j), self.height_with_dropoff(x, y, i, j, height))
        height_map.point(round(x), round(y)).set_biome('ridge')
        return reached_edge
    
    def height_with_dropoff(self, centerX, centerY, x, y, height):
        distance = self.distance(centerX, centerY, x, y)
        if distance > self.width:
            distance = self. width
        return (self.width - distance) * math.pow(self.dropoff, distance) * height / self.width + (random.random() * self.height_max / 5)
    
    def set_height(self, height_map, x, y, height):
        if self.check_point(height_map, x, y) == None or height_map.point(x, y).get_elevation() < self.min_elevation:
            return True
        if height_map.point(x, y).get_elevation() < height:
            height_map.point(x, y).set_elevation(height)
            if height_map.point(x, y).get_biome() != 'ridge':
                height_map.point(x, y).set_biome('mountain')
        return False
    
    def make_foothills(self, height_map):
        direction = (self.direction + 90) % 360
        direction2 = (self.direction - 90) % 360
        self.run_foothill_agent(height_map, height_map.point(round(self.x), round(self.y)).get_elevation(), direction, self.width *2)
        self.run_foothill_agent(height_map, height_map.point(round(self.x), round(self.y)).get_elevation(), direction2, self.width *2)
    
    def run_foothill_agent(self, height_map, height, direction, length):
        x = self.x
        y = self.y
        current_height = height
        reached_edge = False
        turn = True
        for i in range(0, length):
            reached_edge = self.elevate_foothill(height_map, x, y, current_height, self.width / 3)
            if reached_edge:
                break
            if i % round(length / 5) == 0:
                direction = self.turn_foothill(height_map, direction, x, y, turn)
                turn = not turn
            current_height -= height / length
            direction_radian = math.pi * direction / 180
            x = x + math.cos(direction_radian)
            y = y + math.sin(direction_radian)
    
    def turn_foothill(self, height_map, direction, x, y, turn):
        turn_amount = random.randrange(30, 60)
        if turn:
            return (direction - turn_amount) % 360
        else:
            return (direction + turn_amount) % 360
    
    def turn_left(self, hard):
        minimum = 0
        if hard:
            minimum = (self.turn_min + self.turn_max) / 2
        else:
            minimum = self.turn_min
        turn = random.randrange(minimum, self.turn_max)
        self.rotate_agent(-turn)
    
    def turn_right(self, hard):
        minimum = 0
        if hard:
            minimum = (self.turn_min + self.turn_max) / 2
        else:
            minimum = self.turn_min
        turn = random.randrange(minimum, self.turn_max)
        self.rotate_agent(turn)
    
    def rotate_agent(self, amount):
        self.direction = (self.direction + amount) % 360
       
    def get_turn(self):
        turn = random.randrange(self.turn_min, self.turn_max)
        if random.randrange(0, 1) > .5:
            return turn
        else:
            return -turn
    
    def move_agent(self):
        direction_radian = math.pi * self.direction / 180
        newX = self.x + math.cos(direction_radian)
        newY = self.y + math.sin(direction_radian)
        self.x = newX
        self.y = newY
    
    def distance(self, x1, y1, x2, y2):
        return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    