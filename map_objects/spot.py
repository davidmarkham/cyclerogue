from random import sample, choice, randint
from math import sqrt

from config import get_constants
from map_objects.tunnel import Tunnel
from entity_library.monsters import add_monster
from entity_library.items import add_item

constants = get_constants()

class Spot:
    # Used to handle single tile map objects, such as intersections and dead ends (possibly with stuff)
    def __init__(self, x = None, y = None):
        if x == None:
            self.x = randint(1, constants.map_width - 2)
        else:
            self.x = x
        if y == None:
            self.y = randint(1, constants.map_height - 2)
        else:
            self.y = y
        self.tiles = []
        self.place_monster = False
        self.place_item = False

    def center(self):
        return (self.x, self.y)

    def intersect(self, other):
        # returns true if this rectangle intersects with another one
        return (self.x <= other.x2 and self.x >= other.x1 and self.y <= other.y2 and self.y >= other.y1)

    def get_tiles(self):
        return self.tiles

    def get_random_tile(self):
        return (self.x,self.y)

    def create(self, game_map):
        if not game_map.is_blocked(self.x, self.y):
            return False
        # go through the tiles in the rectangle and make them passable
        game_map.tiles[self.x][self.y].blocked = False
        game_map.tiles[self.x][self.y].block_sight = False
        self.tiles.append((self.x,self.y))
        return True

    def connect(self, game_map):
        
        con_up = not game_map.is_blocked(self.x, self.y - 1)
        con_down = not game_map.is_blocked(self.x, self.y + 1)
        con_left = not game_map.is_blocked(self.x - 1, self.y)
        con_right = not game_map.is_blocked(self.x + 1, self.y)

        # Find directions that are connection candidates
        direction_choices = set(())
        up_candidates = []
        if not con_up:
            for room in game_map.rooms:
                if self.y > room.center()[1]:
                    up_candidates.append(room)
                    direction_choices.add('u')
        down_candidates = []
        if not con_up:
            for room in game_map.rooms:
                if self.y < room.center()[1]:
                    down_candidates.append(room)
                    direction_choices.add('d')
        left_candidates = []
        if not con_left:
            for room in game_map.rooms:
                if self.x > room.center()[0]:
                    left_candidates.append(room)
                    direction_choices.add('l')
        right_candidates = []
        if not con_right:
            for room in game_map.rooms:
                if self.x < room.center()[0]:
                    right_candidates.append(room)
                    direction_choices.add('r')
        if len(direction_choices) >= 1:
            number_of_new_connections = randint(1,len(direction_choices))
            connection_dirs = set(sample(direction_choices, number_of_new_connections))
            if 'u' in connection_dirs:
                (target_x, target_y) = choice(up_candidates).get_random_tile()
                new_tunnel = Tunnel(self.x, self.y, target_x, target_y, True)
                new_tunnel.create_tunnel(game_map)
                game_map.tunnels.append(new_tunnel)
                game_map.connected_tiles += new_tunnel.get_tiles()
            if 'd' in connection_dirs:
                (target_x, target_y) = choice(down_candidates).get_random_tile()
                new_tunnel = Tunnel(self.x, self.y, target_x, target_y, True)
                new_tunnel.create_tunnel(game_map)
                game_map.tunnels.append(new_tunnel)
                game_map.connected_tiles += new_tunnel.get_tiles()
            if 'l' in connection_dirs:
                (target_x, target_y) = choice(left_candidates).get_random_tile()
                new_tunnel = Tunnel(self.x, self.y, target_x, target_y, False)
                new_tunnel.create_tunnel(game_map)
                game_map.tunnels.append(new_tunnel)
                game_map.connected_tiles += new_tunnel.get_tiles()
            if 'r' in connection_dirs:
                (target_x, target_y) = choice(right_candidates).get_random_tile()
                new_tunnel = Tunnel(self.x, self.y, target_x, target_y, False)
                new_tunnel.create_tunnel(game_map)
                game_map.tunnels.append(new_tunnel)
                game_map.connected_tiles += new_tunnel.get_tiles()

            if number_of_new_connections == 1 and not (con_up or con_down or con_left or con_right):
                self.place_monster = randint(0,1) == 1
                self.place_item = randint(0,1) == 1   

    def place_entities(self, game_map, entities):

        if self.place_monster and self.place_item:
            # Special Spot
            add_monster(game_map.dungeon_level + constants.special_spot_monster_boost, self.x, self.y, entities)
            add_item(game_map.dungeon_level + constants.special_spot_item_boost, self.x, self.y, entities)
        elif self.place_monster:
            add_monster(game_map.dungeon_level, self.x, self.y, entities)
        elif self.place_item:
            add_item(game_map.dungeon_level, self.x, self.y, entities)