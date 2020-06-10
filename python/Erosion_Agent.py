from Height_Map import Height_Map
from Point import Point
import random
import math
import numpy as np


        
    
class Erosion_Agent:
    def __init__(self):
        self.erosion_radius = 3
        self.inertia = .05
        self.sediment_capacity_factor = 4
        self.min_sediment_capacity = .01
        self.erode_speed = .3
        self.deposit_speed = .3
        self.evaporate_speed = .01
        self.gravity = 4
        self.max_droplet_lifetime = 30
        self.initial_water_volume = 1
        self.initial_speed = 1
        
        self.erosion_brush_indicies = [[]]
        self.erosion_brush_weights = [[]]
        
        self.current_seed = None
        self.current_erosion_radius = 0
        self.current_map_size = 0
    
    def initialize(self, map_size, reset_seed):
        if reset_seed or self.current_seed == None:
            self.current_seed = random.randint(0, 100)
            self.initialize_brush_indicies(map_size, self.erosion_radius)
            self.current_erosion_radius = self.erosion_radius
            self.current_map_size = map_size
    
    def erode(self, height_map, map_size, iterations, reset_seed):
        self.initialize(map_size, reset_seed)
        
        for i in range(0, iterations):
            xpos = random.random() * (map_size - 1)
            ypos = random.random() * (map_size - 1)
            xdir = 0
            ydir = 0
            speed = self.initial_speed
            water = self.initial_water_volume
            sediment = 0
            
            for j in range(0, self.max_droplet_lifetime):
                nodeX = int(xpos)
                nodeY = int(ypos)
                droplet_index = nodeY * map_size + nodeX
                cell_offset_x = xpos - nodeX
                cell_offset_y = ypos - nodeY
                
                # Calculate droplet's height and direction of flow with bilinear interpolation of surrounding heights
                height_and_grad = self.calculate_h_and_g(height_map, map_size, xpos, ypos)
                
                # Update the droplet's direction and position (move position 1 unit regardless of speed)
                xdir = (xdir * self.inertia - height_and_grad[1] * (1 - self.inertia))
                ydir = (ydir * self.inertia - height_and_grad[2] * (1 - self.inertia))
                
                # Normalize direction
                length = math.sqrt(xdir * xdir + ydir * ydir)
                if length != 0:
                    xdir /= length
                    ydir /= length
                
                xpos += xdir
                ypos += ydir
                
                # Stop simulating droplet if it's not moving or has flowed over edge of map
                if (xdir == 0 and ydir == 0) or xpos < 0 or ypos < 0 or xpos > map_size - 1 or ypos > map_size - 1:
                    break
                
                # Find the droplet's new height and calculate the deltaHeight
                new_height_and_grad = self.calculate_h_and_g(height_map, map_size, xpos, ypos)
                new_height = new_height_and_grad[0]
                delta_height = new_height - height_and_grad[0]
                
                # Calculate the droplet's sediment capacity (higher when moving fast down a slope and contains lots of water)
                sediment_capacity = max(-delta_height * speed + water * self.sediment_capacity_factor, self.min_sediment_capacity)
                
                # If carrying more sediment than capacity, or if flowing uphill:
                if sediment > sediment_capacity or delta_height > 0:
                    # If moving uphill (deltaHeight > 0) try fill up to the current height, otherwise deposit a fraction of the excess sediment
                    if delta_height > 0:
                        amount_to_deposit = min(delta_height, sediment)
                    else:
                        amount_to_deposit = (sediment - sediment_capacity) * self.deposit_speed
                    sediment -= amount_to_deposit
                
                    # Add the sediment to the four nodes of the current cell using bilinear interpolation
                    # Deposition is not distributed over a radius (like erosion) so that it can fill small pits
                    height_map.point(nodeX, nodeY).set_elevation(height_map.point(nodeX, nodeY).get_elevation() + amount_to_deposit * (1 - cell_offset_x) * (1 - cell_offset_y))
                    height_map.point(nodeX + 1, nodeY).set_elevation(height_map.point(nodeX, nodeY).get_elevation() + amount_to_deposit * cell_offset_x * (1 - cell_offset_y))
                    height_map.point(nodeX, nodeY + 1).set_elevation(height_map.point(nodeX, nodeY).get_elevation() + amount_to_deposit * (1 - cell_offset_x) * cell_offset_y)
                    height_map.point(nodeX + 1, nodeY + 1).set_elevation(height_map.point(nodeX, nodeY).get_elevation() + amount_to_deposit * cell_offset_x * cell_offset_y)
                else:
                    # Erode a fraction of the droplet's current carry capacity.
                    # Clamp the erosion to the change in height so that it doesn't dig a hole in the terrain behind the droplet
                    amount_to_erode = min((sediment_capacity - sediment) * self.erode_speed, -delta_height)
                    
                    # Use erosion brush to erode from all nodes inside the droplet's erosion radius
                    for k in range(0, len(self.erosion_brush_indicies[droplet_index])):
                        node_index = self.erosion_brush_indicies[droplet_index][k]
                        weighted_erode_amount = amount_to_erode * self.erosion_brush_weights[droplet_index][k]
                        if height_map.point(nodeX, nodeY).get_elevation() < weighted_erode_amount:
                            delta_sediment = height_map.point(nodeX, nodeY).get_elevation()
                        else:
                            delta_sediment = weighted_erode_amount
                        height_map.point(nodeX, nodeY).set_elevation(height_map.point(nodeX, nodeY).get_elevation() - delta_sediment)
                        sediment += delta_sediment
                
                # Update droplet's speed and water content
                speed = math.sqrt(abs(speed * speed + delta_height * self.gravity))
                water *= 1 - self.evaporate_speed
            
    def calculate_h_and_g(self, height_map, map_size, posX, posY):
        coordX = int(posX)
        coordY = int(posY)
        
        # Calculate droplet's offset inside the cell (0,0) = at NW node, (1,1) = at SE node
        x = posX - coordX
        y = posY - coordY
        
        # Calculate heights of the four nodes of the droplet's cell
        height_NW = height_map.point(coordX, coordY).get_elevation()
        height_NE = height_map.point(coordX + 1, coordY).get_elevation()
        height_SW = height_map.point(coordX, coordY + 1).get_elevation()
        height_SE = height_map.point(coordX + 1, coordY + 1).get_elevation()
        
        # Calculate droplet's direction of flow with bilinear interpolation of height difference along the edges
        gradX = (height_NE - height_NW) * (1 - y) + (height_SE - height_SW) * y
        gradY = (height_SW - height_NW) * (1 - x) + (height_SE - height_NE) * x
        
        # Calculate height with bilinear interpolation of the heights of the nodes of the cell
        height = height_NW * (1 - x) * (1 - y) + height_NE * x * (1 - y) + height_SW * (1 - x) * y + height_SE * x * y

        return (height, gradX, gradY)

    def initialize_brush_indicies(self, map_size, radius):
        self.erosion_brush_indicies = [[]]
        self.erosion_brush_weights = [[]]
        for i in range(0, map_size * map_size - 1):
            self.erosion_brush_indicies.append([])
            self.erosion_brush_weights.append([])
        
        xoffsets = np.zeros(radius * radius * 4)
        yoffsets = np.zeros(radius * radius * 4)
        weights = np.zeros(radius * radius * 4)
        weight_sum = 0
        add_index = 0
        
        for i in range(0, map_size * map_size):
            centerX = i % map_size
            centerY = i / map_size
            
            if centerY <= radius or centerY >= map_size - radius or centerX <= radius + 1 or centerX >= map_size - radius:
                weight_sum = 0
                add_index = 0
                for y in range(-radius, radius):
                    for x in range(-radius, radius):
                        sqr_dist = x * x + y * y
                        if sqr_dist < radius * radius:
                            coordX = centerX + x
                            coordY = centerY + y
                            
                            if coordX >= 0 and coordX < map_size and coordY >= 0 and coordY < map_size:
                                weight = 1 - math.sqrt(sqr_dist) / radius
                                weight_sum += weight
                                weights[add_index] = weight
                                xoffsets[add_index] = x
                                yoffsets[add_index] = y
                                add_index += 1
                                
            num_entries = add_index
            self.erosion_brush_indicies[i] = np.zeros(num_entries)
            self.erosion_brush_weights[i] = np.zeros(num_entries)
            
            for j in range(0, num_entries):
                self.erosion_brush_indicies[i][j] = (yoffsets[j] + centerY) * map_size + xoffsets[j] + centerX
                self.erosion_brush_weights[i][j] = weights[j] / weight_sum




