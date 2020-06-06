import math

class Point:
    def __init__(self, elevation, biome, xpos, ypos):
        self.elevation = elevation
        self.biome = biome
        self.x = xpos
        self.y = ypos
    
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
    
    def get_elevation(self):
        return self.elevation
    
    def get_biome(self):
        return self.biome
    
    def set_elevation(self, elevation):
        self.elevation = elevation
    
    def set_biome(self, biome):
        self.biome = biome
    
    def dist(self, point):
        x1 = self.x
        y1 = self.y
        x2 = point.getX()
        y2 = point.getY()
        return math.sqrt(((x1 - x2) * (x1 - x2)) + ((y1 - y2) * (y1 - y2)))
    
    def dir(self, point):
        x1 = self.x
        y1 = self.y
        x2 = point.getX()
        y2 = point.getY()
        print("We actually used point.dir")
        return 'We actually used point.dir'
    
    def __str__(self):
        return "Point: (" + str(self.x) + ", " + str(self.y) + ") \nElevation: " + str(self.elevation) + "\nBiome: " + self.biome