import tcod
from random import randint, sample, choice
from math import sqrt

from components.fighter import Fighter
from components.item import Item
from components.stairs import Stairs
from components.ai import BasicMonster, SmartMonster
from equipment_slots import EquipmentSlots
from components.equippable import Equippable
from entity import Entity
from game_messages import Message
from item_functions import heal, cast_lightning, cast_fireball, cast_confuse
from map_objects.tile import Tile
from map_objects.rectangle import Rect
from map_objects.tunnel import Tunnel
from render_functions import RenderOrder
from random_utils import random_choice_from_dict, from_dungeon_level
from entity_library.monsters import add_monsters_to_room
from entity_library.items import add_items_to_room


class GameMap:
    def __init__(self, constants, dungeon_level=1):
        self.width = constants.map_width
        self.height = constants.map_height
        self.tiles = self.initialize_tiles()

        self.dungeon_level = dungeon_level

        self.view_x_min = None
        self.view_y_min = None
        self.view_x_max = None
        self.view_y_max = None
    
    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def make_map(self, constants, player, entities):
        
        rooms = []
        tunnels = []
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range(constants.max_rooms):
            # Randomly generate rooms
            w = randint(constants.room_min_size, constants.room_max_size)
            h = randint(constants.room_min_size, constants.room_max_size)
            x = randint(0, constants.map_width - w - 1)
            y = randint(0, constants.map_height - h - 1)
            
            # Using Rect class for rooms
            new_room = Rect(x, y, w, h)

            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # if the for loop doesn't get broken out of
                # paint the map tiles
                self.create_room(new_room)

                # center coordinates of new room, will be useful later
                (new_x, new_y) = new_room.center()

                center_of_last_room_x = new_x
                center_of_last_room_y = new_y

                if num_rooms == 0:
                    # start player in first room
                    player.x = new_x
                    player.y = new_y
                    self.set_view_range(player, constants)
                else:
                    # for subsequent rooms, connect the current one to the nearest one  if it doesn't already touch a tunnel

                    # check to see if any of the walls are not blocked
                    connected = False
                    for i in range(x, x + w):
                        if not self.tiles[i][y].blocked:
                            connected = True
                            break
                        if y + h + 1 < constants.map_height:
                            if not self.tiles[i][y+h+1].blocked:
                                connected = True
                                break

                    if not connected:
                        for i in range(y, y + h):
                            if not self.tiles[x][i].blocked:
                                connected = True
                                break
                            if x + w + 1 < constants.map_width:
                                if  not self.tiles[x+w+1][i].blocked:
                                    connected = True
                                    break

                    if not connected:
                        # find the nearest room
                        nearest_distance = 9999
                        nearest_room = rooms[0]
                        if len(rooms) > 1:
                            for room in rooms:
                                (room_x, room_y) = room.center()
                                distance = sqrt((new_x - room_x) ** 2 + (new_y - room_y) ** 2)
                                if distance < nearest_distance:
                                    nearest_distance = distance
                                    nearest_room = room
                        (target_x, target_y) = nearest_room.get_random_tile()
                        (new_x, new_y) = new_room.get_random_tile()
                        if randint(0,1) == 1:
                            # horizontal then vertical
                            self.create_tunnel(target_x, target_y, new_x, new_y, False)
                            tunnels.append(Tunnel(target_x, target_y, new_x, new_y, False))
                        else:
                            # vertical then horizontal
                            self.create_tunnel(target_x, target_y, new_x, new_y, True)
                            tunnels.append(Tunnel(target_x, target_y, new_x, new_y, True))

                self.place_entities(new_room, entities)

                # add room to list and increment counter
                rooms.append(new_room)
                num_rooms +=1

        stairs_component = Stairs(self.dungeon_level + 1)
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '>', tcod.white, 'Stairs', render_order=RenderOrder.STAIRS, stairs=stairs_component)
        entities.append(down_stairs)

        # add some extra tunnels
        for i in range(randint(constants.min_extra_tunnels, constants.max_extra_tunnels)):
            if randint(0,100) < constants.chance_extra_tunnel_from_tunnel:
                selected_room1 = choice(tunnels)
            else:
                selected_room1 = choice(rooms)

            (x1, y1) = selected_room1.get_random_tile()   
            if randint(0,100) > constants.random_point_tunnel_chance: 
                if randint(0,100) < constants.chance_extra_tunnel_from_tunnel:
                    selected_room2 = choice(tunnels)
                else:
                    selected_room2 = choice(rooms)
                (x2, y2) = selected_room2.get_random_tile()
            else:
                # Pick a random blocked point
                x2 = randint(1, constants.map_width - w - 1)
                y2 = randint(1, constants.map_height - h - 1)
                while not self.tiles[x2][y2].blocked:
                    x2 = randint(1, constants.map_width - w - 1)
                    y2 = randint(1, constants.map_height - h - 1)
            if randint(0,1) == 1:
                # horizontal then vertical
                self.create_tunnel(x1, y1, x2, y2, False)
                tunnels.append(Tunnel(x1, y1, x2, y2, False))
            else:
                # vertical then horizontal
                self.create_tunnel(x1, y1, x2, y2, True)
                tunnels.append(Tunnel(x1, y1, x2, y2, True))


    def create_room(self, room):
        # go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_tunnel(self, x1, y1, x2, y2, vertical_first):
        if vertical_first:
            # vertical then horizontal
            self.create_v_tunnel(y1, y2, x1)
            self.create_h_tunnel(x1, x2, y2)
        else:
            # horizontal then vertical
            self.create_h_tunnel(x1, x2, y1)
            self.create_v_tunnel(y1, y2, x2)


    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2)+1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2)+1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def place_entities(self, room, entities):
        #add_monsters_to_room(self.dungeon_level, room, entities)
        add_items_to_room(self.dungeon_level, room, entities)

        
    
    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False

    def next_floor(self, player, message_log, constants):
        self.dungeon_level += 1
        entities = [player]
        self.tiles = self.initialize_tiles()
        self.make_map(constants, player, entities)

        player.fighter.heal(player.fighter.max_hp // 2)

        message_log.add_message(Message('You take a moment to rest, and recover your strength.', tcod.light_violet))

        return entities

    def set_view_range(self, player, constants):
        self.view_x_min = player.x - constants.view_width // 2
        self.view_y_min = player.y - constants.view_height // 2
        
        #Check to set view to be within range if it is out of range
        if self.view_x_min < 0:
            self.view_x_min = 0
        if self.view_y_min < 0:
            self.view_y_min = 0
        if self.view_x_min + constants.view_width > self.width:
            self.view_x_min = self.width - constants.view_width
        if self.view_y_min + constants.view_height > self.height:
            self.view_y_min = self.height - constants.view_height

        self.view_x_max = self.view_x_min + constants.view_width
        self.view_y_max = self.view_y_min + constants.view_height
