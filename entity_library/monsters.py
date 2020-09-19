import tcod
from random import randint
from copy import deepcopy

from components.fighter import Fighter
from entity import Entity
from render_functions import RenderOrder
from components.ai import BasicMonster, SmartMonster
from random_utils import from_dungeon_level, random_choice_from_dict
from monster_functions import *
from config import get_constants

constants = get_constants()

class Monster:
    def __init__(self, name, char, color, hp, power, defense, xp, occurance, ai_component = BasicMonster()):
        self.name = name
        self.char = char
        self.color = color
        self.hp = hp
        self.power = power
        self.defense = defense
        self.xp = xp
        self.ai_component = ai_component
        self.occurance = occurance

        self.fighter_component = Fighter(hp=self.hp, defense=self.defense, power=self.power, xp=self.xp)

    def get_chance(self, dungeon_level):
        return {self: from_dungeon_level(self.occurance, dungeon_level)}

    def generate(self, x, y):
        return Entity(x, y, self.char, self.color, self.name, blocks=True, fighter=deepcopy(self.fighter_component), ai=deepcopy(self.ai_component), render_order=RenderOrder.ACTOR)


monster_library = [
    Monster('Kobold', 'k', tcod.desaturated_purple, 20, 4, 0, 35, [[80, 1]], ai_component=SmartMonster()),
    Monster('Orc', 'o', tcod.desaturated_green, 30, 8, 2, 100, [[15, 3], [30, 5], [60, 7]], ai_component=SmartMonster()),
    Monster('Troll', 'T', tcod.darker_green, 50, 12, 3, 300, [[5, 5], [15, 7], [30, 10]], ai_component=SmartMonster(on_turn=[regeneration], function_params={'regen_rate':1})),
]

monsters_by_level = [[2, 1], [3, 4], [5, 6]]

def get_monster_chances(dungeon_level):
    monster_chances = {}
    for monster in monster_library:
        monster_chances.update(monster.get_chance(dungeon_level))
    return monster_chances
        
def add_monsters_to_room(dungeon_level, room, entities):
    if constants.no_monsters:
        return None
    max_monsters_per_room = from_dungeon_level(monsters_by_level , dungeon_level)
    number_of_monsters = randint(0, max_monsters_per_room)
    
    monster_chances = get_monster_chances(dungeon_level)
    for i in range(number_of_monsters):
            # randomize location
            (x,y) = room.get_random_tile()

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                monster_choice = random_choice_from_dict(monster_chances)
                entities.append(monster_choice.generate(x,y))

def add_monster(dungeon_level, x, y, entities):
    if constants.no_monsters:
        return None
    monster_chances = get_monster_chances(dungeon_level)
    monster_choice = random_choice_from_dict(monster_chances)
    entities.append(monster_choice.generate(x,y))