from random import choice
from math import copysign

class Tunnel:
    def __init__(self, x1, y1, x2, y2, vertFirst):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.vertFirst = vertFirst

    def get_tiles(self):
        tiles = []
        if self.vertFirst:
            for y in range(self.y1, self.y2, int(copysign(1, self.y2 - self.y1))):
                tiles.append((self.x1, y))
            for x in range(self.x1, self.x2, int(copysign(1, self.x2 - self.x1))):
                tiles.append((x, self.y2))
        else:
            for x in range(self.x1, self.x2, int(copysign(1, self.x2 - self.x1))):
                tiles.append((x, self.y1))
            for y in range(self.y1, self.y2, int(copysign(1, self.y2 - self.y1))):
                tiles.append((self.x2, y))
        return tiles

    def get_random_tile(self):
        tiles = self.get_tiles()
        return choice(tiles)