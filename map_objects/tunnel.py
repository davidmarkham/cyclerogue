from random import choice, choices, randint
from math import copysign

class Tunnel:
    def __init__(self, x1, y1, x2, y2, vertFirst):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.vertFirst = vertFirst
        self.tiles = []

    def get_tiles(self):
        return self.tiles

    def get_random_tile(self):
        return choice(self.tiles)

    def create_tunnel(self, game_map):
        # Check to see if it's a straight line tunnel
        if self.x1 == self.x2:
            self.create_v_tunnel(self.y1, self.y2, self.x1, game_map)
            return None
        if self.y1 == self.y2:
            self.create_h_tunnel(self.x1, self.x2, self.y1, game_map)
            return None
        
        # Calculate number of segments
        number_of_segments = randint(0, int(self.get_distance()/10))
        x_coords = choices(range(self.x1, self.x2, int(copysign(1,self.x2-self.x1))), k=number_of_segments)
        y_coords = choices(range(self.y1, self.y2, int(copysign(1,self.y2-self.y1))), k=number_of_segments)
        if self.vertFirst:
            y_coords.sort(reverse=self.y1>self.y2)
        else:
            x_coords.sort(reverse=self.x1>self.x2)
        coords = []
        for i in range(number_of_segments):
            coords.append((x_coords[i],y_coords[i]))
        coords.append((self.x2, self.y2))
        x = self.x1
        y = self.y1
        if self.vertFirst:
            # vertical then horizontal
            for target_coords in coords:
                (x_target, y_target) = target_coords
                if self.create_v_tunnel(y, y_target, x, game_map):
                    break
                if self.create_h_tunnel(x, x_target, y_target, game_map):
                    break
                (x, y) = target_coords
        else:
            # horizontal then vertical
            for target_coords in coords:
                (x_target, y_target) = target_coords
                if self.create_h_tunnel(x, x_target, y, game_map):
                    break
                if self.create_v_tunnel(y, y_target, x_target, game_map):
                    break
                (x, y) = target_coords


    def create_h_tunnel(self, x1, x2, y, game_map):
        for x in range(x1, x2, int(copysign(1,x2-x1))):
            if (x,y) not in game_map.connected_tiles:
                game_map.tiles[x][y].blocked = False
                game_map.tiles[x][y].block_sight = False
                self.tiles.append((x,y))
            elif self.tiles != []:
                self.x2 = x
                self.y2 = y
                return True
            

    def create_v_tunnel(self, y1, y2, x, game_map):
        for y in range(y1, y2, int(copysign(1,y2-y1))):
            if (x,y) not in game_map.connected_tiles:
                game_map.tiles[x][y].blocked = False
                game_map.tiles[x][y].block_sight = False
                self.tiles.append((x,y))
            elif self.tiles != []:
                self.x2 = x
                self.y2 = y
                return True
            
    def get_distance(self):
        return abs(self.x1-self.x2)+abs(self.y1-self.y2)