import tcod

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

    # Debug flags - Should all be False for normal play
    no_clipping = False
    reveal_map = False
    see_all = False
    show_coordinates = False
    no_monsters = False
    no_items = False
    ignore_damage = False

constants = Constants()

def get_constants():
    return constants