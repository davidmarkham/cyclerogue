import tcod as libtcod
from random import randint
from math import sqrt

from components.fighter import Fighter
from components.item import Item
from components.stairs import Stairs
from components.ai import BasicMonster
from equipment_slots import EquipmentSlots
from components.equippable import Equippable
from entity import Entity
from game_messages import Message
from item_functions import heal, cast_lightning, cast_fireball, cast_confuse
from map_objects.tile import Tile
from map_objects.rectangle import Rect
from render_functions import RenderOrder
from random_utils import random_choice_from_dict, from_dungeon_level


class GameMap:
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

        self.dungeon_level = dungeon_level
    
    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities):
        
        rooms = []
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range(max_rooms):
            # Randomly generate rooms
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)
            
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
                else:
                    # for subsequent rooms, connect the current one to the nearest one  if it doesn't already touch a tunnel

                    # check to see if any of the walls are not blocked
                    connected = False
                    for i in range(x, x + w):
                        if not self.tiles[i][y].blocked:
                            connected = True
                            break
                        if y + h + 1 < map_height:
                            if not self.tiles[i][y+h+1].blocked:
                                connected = True
                                break

                    if not connected:
                        for i in range(y, y + h):
                            if not self.tiles[x][i].blocked:
                                connected = True
                                break
                            if x + w + 1 < map_width:
                                if  not self.tiles[x+w+1][i].blocked:
                                    connected = True
                                    break

                    if not connected:
                        # find the nearest room
                        (nearest_x, nearest_y) = rooms[0].center()
                        nearest_distance = 9999
                        if len(rooms) > 1:
                            for room in rooms:
                                (room_x, room_y) = room.center()
                                distance = sqrt((new_x - room_x) ** 2 + (new_y - room_y) ** 2)
                                if distance < nearest_distance:
                                    nearest_distance = distance
                                    nearest_x = room_x
                                    nearest_y = room_y

                        if randint(0,1) == 1:
                            # horizontal then vertical
                            self.create_h_tunnel(nearest_x, new_x, nearest_y)
                            self.create_v_tunnel(nearest_y, new_y, new_x)
                        else:
                            # vertical then horizontal
                            self.create_v_tunnel(nearest_y, new_y, nearest_x)
                            self.create_h_tunnel(nearest_x, new_x, new_y)

                self.place_entities(new_room, entities)

                # add room to list and increment counter
                rooms.append(new_room)
                num_rooms +=1

        stairs_component = Stairs(self.dungeon_level + 1)
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '>', libtcod.white, 'Stairs', render_order=RenderOrder.STAIRS, stairs=stairs_component)
        entities.append(down_stairs)
                        


    def create_room(self, room):
        # go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2)+1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2)+1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def place_entities(self, room, entities):
        # get a random number of monsters
        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.dungeon_level)
        max_items_per_room = from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)

        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)

        monster_chances = {
            'orc': 80, 
            'troll': from_dungeon_level([[15, 3], [30, 5], [60, 7]], self.dungeon_level)
        }
        
        item_chances = {
            'healing_potion': 35,
            'sword': from_dungeon_level([[5, 4]], self.dungeon_level),
            'shield': from_dungeon_level([[15, 8]], self.dungeon_level),
            'lightning_scroll': from_dungeon_level([[25, 4]], self.dungeon_level),
            'fireball_scroll': from_dungeon_level([[25, 6]], self.dungeon_level),
            'confusion_scroll': from_dungeon_level([[10, 2]], self.dungeon_level)
        }

        for i in range(number_of_monsters):
            # randomize location
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                monster_choice = random_choice_from_dict(monster_chances)
                if monster_choice == 'orc':
                    fighter_component = Fighter(hp=20, defense=0, power=4, xp=35)
                    ai_component = BasicMonster()
                    monster = Entity(x, y, 'o', libtcod.desaturated_green, 'Orc', blocks=True, fighter=fighter_component, ai=ai_component, render_order=RenderOrder.ACTOR)
                elif monster_choice == 'troll':
                    fighter_component = Fighter(hp=30, defense=2, power=8, xp=100)
                    ai_component = BasicMonster()
                    monster = Entity(x, y, 'T', libtcod.darker_green, 'Troll', blocks=True, fighter=fighter_component, ai=ai_component, render_order=RenderOrder.ACTOR)
            
                entities.append(monster)

            for i in range(number_of_items):
                x = randint(room.x1 + 1, room.x2 - 1)
                y = randint(room.y1 + 1, room.y2 - 1)

                if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                    item_choice = random_choice_from_dict(item_chances)
                    
                    if item_choice == 'healing_potion':
                        item_component = Item(use_function=heal, amount = 40)
                        item = Entity(x, y, '!', libtcod.violet, 'Healing Potion', render_order=RenderOrder.ITEM, item=item_component)
                    elif item_choice == 'sword':
                        equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
                        item = Entity(x, y, '/', libtcod.sky, 'Sword', equippable=equippable_component)
                    elif item_choice=='shield':
                        equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=1)
                        item = Entity(x, y, '[', libtcod.darker_orange, 'Shield', equippable=equippable_component)
                    elif item_choice == 'fireball_scroll':
                        item_component = Item(use_function=cast_fireball, targeting=True, targeting_message=Message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan), damage=25, radius=3)
                        item = Entity(x, y, '#', libtcod.red, 'Fireball Scroll', render_order=RenderOrder.ITEM, item=item_component)
                    elif item_choice == 'confusion_scroll':
                        item_component = Item(use_function=cast_confuse, targeting=True, targeting_message=Message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan))
                        item = Entity(x, y, '#', libtcod.light_pink, 'Confusion Scroll', render_order=RenderOrder.ITEM, item=item_component)
                    elif item_choice == 'lightning_scroll':
                        item_component = Item(use_function=cast_lightning, damage=40, maximum_range=5)
                        item = Entity(x, y, '#', libtcod.yellow, 'Lightning Scroll', render_order=RenderOrder.ITEM, item=item_component)

                    entities.append(item)
    
    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False

    def next_floor(self, player, message_log, constants):
        self.dungeon_level += 1
        entities = [player]
        self.tiles = self.initialize_tiles()
        self.make_map(constants.max_rooms, constants.room_min_size, constants.room_max_size, constants.map_width, constants.map_height, player, entities)

        player.fighter.heal(player.fighter.max_hp // 2)

        message_log.add_message(Message('You take a moment to rest, and recover your strength.', libtcod.light_violet))

        return entities