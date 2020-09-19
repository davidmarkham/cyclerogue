import tcod
from random import randint
from copy import deepcopy

from entity import Entity
from components.item import Item
from components.equippable import Equippable
from equipment_slots import EquipmentSlots
from render_functions import RenderOrder
from random_utils import from_dungeon_level, random_choice_from_dict
from item_functions import *
from config import get_constants

constants = get_constants()

class Item_Template:
    def __init__(self, name, char, color, occurance, use_function=None, targeting=False, targeting_message=None, equippable=None, stackable=False, **kwargs):
        self.name = name
        self.char = char
        self.color = color
        self.occurance = occurance
        self.use_function = use_function
        self.targeting = targeting
        self.targeting_message = targeting_message
        self.equippable = equippable
        self.stackable = stackable
        self.use_kwargs = kwargs
        if use_function:
            self.item = Item(stackable=self.stackable, use_function=self.use_function, targeting=targeting, targeting_message=targeting_message, charges=kwargs.get('charges'), use_kwargs = self.use_kwargs)
        else:
            self.item = None
        

    def get_chance(self, dungeon_level):
        return {self: from_dungeon_level(self.occurance, dungeon_level)}

    def generate(self, x, y):
        return Entity(x, y, self.char, self.color, self.name, item=deepcopy(self.item), equippable=deepcopy(self.equippable), render_order=RenderOrder.ITEM)


item_library = [
    Item_Template('Healing Potion', '!', tcod.violet, [[35, 1]], use_function=heal, amount=40, stackable=True),
    Item_Template('Sword', '|', tcod.sky, [[5, 4]], equippable=Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)),
    Item_Template('Shield', '[', tcod.darker_orange, [[15, 8]], equippable=Equippable(EquipmentSlots.OFF_HAND, defense_bonus=3)),
    Item_Template('Fireball Scroll', '#', tcod.red, [[25, 6]], use_function=cast_fireball, stackable=True, targeting=True, targeting_message=Message('Left-click a target tile for the fireball, or right-click to cancel.', tcod.light_cyan), damage=25, radius=3),
    Item_Template('Confusion Scroll', '#', tcod.light_pink, [[10, 2]], use_function=cast_confuse, stackable=True, targeting=True, targeting_message=Message('Left-click an enemy to confuse it, or right-click to cancel.', tcod.light_cyan)),
    Item_Template('Lightning Scroll', '#', tcod.yellow, [[25, 4]], use_function=cast_lightning, stackable=True, damage=40, maximum_range=5),
    Item_Template('Lightning Wand', '-', tcod.yellow, [[5 ,6]], use_function=wand, cast_function=cast_lightning, damage=40, maximum_range=5, charges=10)
]

items_by_level = [[1, 1], [2, 4]]

def get_item_chances(dungeon_level):
    item_chances = {}
    for item in item_library:
        item_chances.update(item.get_chance(dungeon_level))
    return item_chances
        
def add_items_to_room(dungeon_level, room, entities):
    if constants.no_items:
        return None
    max_items_per_room = from_dungeon_level(items_by_level, dungeon_level)
    number_of_items = randint(0, max_items_per_room)
    
    item_chances = get_item_chances(dungeon_level)
    for i in range(number_of_items):
            # randomize location
            (x, y) = room.get_random_tile()

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item_choice = random_choice_from_dict(item_chances)
                entities.append(item_choice.generate(x,y))

def add_item(dungeon_level, x, y, entities):
    if constants.no_items:
        return None
    item_chances = get_item_chances(dungeon_level)
    item_choice = random_choice_from_dict(item_chances)
    entities.append(item_choice.generate(x,y))
                
   
