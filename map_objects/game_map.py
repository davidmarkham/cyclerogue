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
from map_objects.spot import Spot
from map_objects.tunnel import Tunnel
from render_functions import RenderOrder
from random_utils import random_choice_from_dict, from_dungeon_level
from entity_library.monsters import add_monsters_to_room
from entity_library.items import add_items_to_room
from config import get_constants

constants = get_constants()


class GameMap:
    def __init__(self, dungeon_level=1):
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

    def make_map(self, player, entities):
        
        self.rooms = []
        self.tunnels = []
        self.connected_tiles = []
        self.spots = []
        
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range(constants.max_rooms):
            # Using Rect class for rooms
            new_room = Rect()

            if new_room.create(self):
                # Create the room

                if num_rooms == 0:
                    # start player in first room
                    (new_x, new_y) = new_room.center()
                    player.x = new_x
                    player.y = new_y
                    self.set_view_range(player)
                else:
                    new_room.connect(self)

                new_room.place_entities(self, entities)

                # add room to list and increment counter
                self.rooms.append(new_room)
                self.connected_tiles += new_room.get_tiles()
                num_rooms +=1

        for r in range(constants.max_spots):
            new_spot = Spot()
            if new_spot.create(self):
                new_spot.connect(self)
                new_spot.place_entities(self, entities)
                self.spots.append(new_spot)
                self.connected_tiles.extend(new_spot.get_tiles())

        stairs_component = Stairs(self.dungeon_level + 1)
        (center_of_last_room_x, center_of_last_room_y) = self.rooms[-1].center()
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '>', tcod.white, 'Stairs', render_order=RenderOrder.STAIRS, stairs=stairs_component)
        entities.append(down_stairs)

    
    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False

    def next_floor(self, player, message_log):
        self.dungeon_level += 1
        entities = [player]
        self.tiles = self.initialize_tiles()
        self.make_map(player, entities)

        player.fighter.heal(player.fighter.max_hp // 2)

        message_log.add_message(Message('You take a moment to rest, and recover your strength.', tcod.light_violet))

        return entities

    def set_view_range(self, player):
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
