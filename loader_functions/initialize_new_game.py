import tcod

from components.fighter import Fighter
from components.inventory import Inventory
from components.equipment import Equipment
from components.equippable import Equippable
from components.level import Level
from entity import Entity
from game_messages import MessageLog
from game_states import GameStates
from map_objects.game_map import GameMap
from render_functions import RenderOrder
from equipment_slots import EquipmentSlots
from config import get_constants

constants = get_constants()


def get_game_variables():
    fighter_component = Fighter(hp=100, defense=1, power=2)
    inventory_conponent = Inventory(26)
    level_component = Level()
    equipment_component = Equipment()

    player = Entity(0, 0, '@', tcod.white, 'Player', blocks=True, fighter=fighter_component, inventory=inventory_conponent, render_order=RenderOrder.ACTOR, level=level_component, equipment=equipment_component)
    entities = [player]

    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
    dagger = Entity(0, 0, '-', tcod.sky, 'Dagger', equippable=equippable_component)
    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)

    game_map = GameMap()
    game_map.make_map(player, entities)

    message_log = MessageLog(constants.message_x, constants.message_width, constants.message_height)

    game_state = GameStates.PLAYERS_TURN

    return player, entities, game_map, message_log, game_state

