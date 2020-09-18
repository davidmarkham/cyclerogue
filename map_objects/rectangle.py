from random import choice, randint
from math import sqrt

from config import get_constants
from map_objects.tunnel import Tunnel
from entity_library.monsters import add_monsters_to_room
from entity_library.items import add_items_to_room

constants = get_constants()

class Rect:
    def __init__(self, x = None, y = None, w = None, h = None):
        if w == None:
            w = randint(constants.room_min_size, constants.room_max_size)
        if h == None:
            h = randint(constants.room_min_size, constants.room_max_size)
        if x == None:
            self.x1 = randint(0, constants.map_width - w - 1)
        else:
            self.x1 = x
        if y == None:
            self.y1 = randint(0, constants.map_height - h - 1)
        else:
            self.y1 = y
        self.x2 = self.x1 + w
        self.y2 = self.y1 + h
        self.tiles = []

    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)

    def intersect(self, other):
        # returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1)

    def get_tiles(self):
        return self.tiles

    def get_random_tile(self):
        return choice(self.tiles)

    def create(self, game_map):
        # go through the tiles in the rectangle and make them passable
        for x in range(self.x1 + 1, self.x2):
            for y in range(self.y1 + 1, self.y2):
                game_map.tiles[x][y].blocked = False
                game_map.tiles[x][y].block_sight = False
                self.tiles.append((x,y))

    def connect(self, game_map):
        connected = False
        for i in range(self.x1, self.x2):
            if not game_map.tiles[i][self.y1].blocked:
                connected = True
                break
            if self.y2 + 1 < constants.map_height:
                if not game_map.tiles[i][self.y2].blocked:
                    connected = True
                    break

        if not connected:
            for i in range(self.y1, self.y2):
                if not game_map.tiles[self.x1][i].blocked:
                    connected = True
                    break
                if self.x2 + 1 < constants.map_width:
                    if  not game_map.tiles[self.x2][i].blocked:
                        connected = True
                        break

        if not connected:
            # find the nearest room
            nearest_distance = 9999
            nearest_room = game_map.rooms[0]
            (new_x, new_y) = self.center()
            if len(game_map.rooms) > 1:
                for room in game_map.rooms:
                    (room_x, room_y) = room.center()
                    distance = sqrt((new_x - room_x) ** 2 + (new_y - room_y) ** 2)
                    if distance < nearest_distance:
                        nearest_distance = distance
                        nearest_room = room
            (target_x, target_y) = nearest_room.get_random_tile()
            (new_x, new_y) = self.get_random_tile()
            if randint(0,1) == 1:
                # horizontal then vertic
                new_tunnel = Tunnel(new_x, new_y, target_x, target_y, False)
                new_tunnel.create_tunnel(game_map)
                game_map.tunnels.append(new_tunnel)
                game_map.connected_tiles += new_tunnel.get_tiles()
            else:
                # vertical then horizontal
                new_tunnel = Tunnel(new_x, new_y, target_x, target_y, True)
                new_tunnel.create_tunnel(game_map)
                game_map.tunnels.append(new_tunnel)
                game_map.connected_tiles += new_tunnel.get_tiles()

    def place_entities(self, game_map, entities):
        add_monsters_to_room(game_map.dungeon_level, self, entities)
        add_items_to_room(game_map.dungeon_level, self, entities)