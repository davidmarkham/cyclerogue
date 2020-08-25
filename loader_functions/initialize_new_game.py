import tcod as libtcod

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

class Constants:
    window_title = 'CycleRogue'
    
    screen_width = 80
    screen_height = 50
    
    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    colors = {
        'dark_wall': libtcod.Color(0, 0, 100),
        'dark_ground': libtcod.Color(50, 50, 150),
        'light_wall': libtcod.Color(130, 110, 50),
        'light_ground': libtcod.Color(200, 180, 50)
    }

def get_game_variables():
    fighter_component = Fighter(hp=100, defense=1, power=2)
    inventory_conponent = Inventory(26)
    level_component = Level()
    equipment_component = Equipment()

    player = Entity(0, 0, '@', libtcod.white, 'Player', blocks=True, fighter=fighter_component, inventory=inventory_conponent, render_order=RenderOrder.ACTOR, level=level_component, equipment=equipment_component)
    entities = [player]

    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
    dagger = Entity(0, 0, '-', libtcod.sky, 'Dagger', equippable=equippable_component)
    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)

    game_map = GameMap(Constants.map_width, Constants.map_height)
    game_map.make_map(Constants.max_rooms, Constants.room_min_size, Constants.room_max_size, Constants.map_width, Constants.map_height, player, entities)

    message_log = MessageLog(Constants.message_x, Constants.message_width, Constants.message_height)

    game_state = GameStates.PLAYERS_TURN

    return player, entities, game_map, message_log, game_state