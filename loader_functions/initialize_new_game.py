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

    map_width = 100
    map_height = 100

    view_width = 80
    view_height = 43

    # Map Generation Parameters
    room_max_size = 10
    room_min_size = 6
    max_rooms = 25
    min_extra_tunnels = 5
    max_extra_tunnels = 10
    chance_extra_tunnel_from_tunnel = 80 # Percent
    random_point_tunnel_chance = 75 # Percent

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    colors = {
        'dark_wall': tcod.Color(0, 0, 100),
        'dark_ground': tcod.Color(50, 50, 150),
        'light_wall': tcod.Color(130, 110, 50),
        'light_ground': tcod.Color(200, 180, 50)
    }

    #Debug flags
    no_clipping = True
    reveal_map = True
    show_coordinates = True

def get_game_variables(constants):
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

    game_map = GameMap(constants)
    game_map.make_map(constants, player, entities)

    message_log = MessageLog(Constants.message_x, Constants.message_width, Constants.message_height)

    game_state = GameStates.PLAYERS_TURN

    return player, entities, game_map, message_log, game_state