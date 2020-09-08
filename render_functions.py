import tcod

from enum import Enum, auto

from game_states import GameStates
from menus import inventory_menu, level_up_menu, character_screen

class RenderOrder(Enum):
    STAIRS = auto()
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()

def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)

    names = [entity.display_name for entity in entities if entity.x == x and entity.y == y and tcod.map_is_in_fov(fov_map, entity.x, entity.y)]
    names = ', '.join(names)

    return names.capitalize()

def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    tcod.console_set_default_background(panel, back_color)
    tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_foreground(panel, tcod.white)
    tcod.console_print_ex(panel, int(x+total_width / 2), y, tcod.BKGND_NONE, tcod.CENTER, f'{name}: {value}/{maximum}')

def render_all(con, panel, mouse, entities, player, game_map, fov_map, fov_recompute, message_log, game_state, constants):
    # Check to see if the view window needs updating
    if ((player.x < game_map.view_x_min + constants.view_width // 4 and game_map.view_x_min > 0) or 
        (player.y < game_map.view_y_min + constants.view_height // 4 and game_map.view_y_min > 0) or 
        (player.x > game_map.view_x_max - constants.view_width // 4 and game_map.view_x_max < game_map.width) or 
        (player.y > game_map.view_y_max - constants.view_height // 4 and game_map.view_y_max < game_map.height)):
        game_map.set_view_range(player, constants)
        # clear the view window
        tcod.console_clear(con)

    
    if fov_recompute:
        # Draw all the tiles in the view
        for y in range(game_map.view_y_min, game_map.view_y_max):
            for x in range(game_map.view_x_min, game_map.view_x_max):
                #visible = tcod.map_is_in_fov(fov_map, x, y)
                visible = True
                wall = game_map.tiles[x][y].block_sight
                if visible:
                    if wall:
                        tcod.console_set_char_background(con, x - game_map.view_x_min, y - game_map.view_y_min, constants.colors.get('light_wall'), tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(con, x - game_map.view_x_min, y - game_map.view_y_min, constants.colors.get('light_ground'), tcod.BKGND_SET)
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    if wall:
                        tcod.console_set_char_background(con, x - game_map.view_x_min, y - game_map.view_y_min, constants.colors.get('dark_wall'), tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(con, x - game_map.view_x_min, y - game_map.view_y_min, constants.colors.get('dark_ground'), tcod.BKGND_SET)

            
    # Draw all entities in the list
    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)
    
    for entity in entities_in_render_order:
        draw_entity(con, entity, fov_map, game_map)
        
    tcod.console_blit(con, 0, 0, constants.screen_width, constants.screen_height, 0, 0, 0)

    tcod.console_set_default_background(panel, tcod.black)
    tcod.console_clear(panel)

    # Print the message log, line by line
    y = 1
    for message in message_log.messages:
        tcod.console_set_default_foreground(panel, message.color)
        tcod.console_print_ex(panel, message_log.x, y, tcod.BKGND_NONE, tcod.LEFT, message.text)
        y += 1

    render_bar(panel, 1, 1, constants.bar_width, 'HP', player.fighter.hp, player.fighter.max_hp, tcod.light_red, tcod.darker_red)
    tcod.console_print_ex(panel, 1, 3, tcod.BKGND_NONE, tcod.LEFT, f'Dungeon Level: {game_map.dungeon_level}')

    tcod.console_set_default_foreground(panel, tcod.light_gray)
    tcod.console_print_ex(panel, 1, 0, tcod.BKGND_NONE, tcod.LEFT, get_names_under_mouse(mouse, entities, fov_map))

    tcod.console_blit(panel, 0, 0, constants.screen_width, constants.panel_height, 0, 0, constants.panel_y)

    if game_state in (game_state.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = 'Press the key next to an item to use it, or Esc to cancel\n'
        else:
            inventory_title = 'Press the key next to an item to drop it, or Esc to cancel\n'
        inventory_menu(con, inventory_title, player, 50, constants)

    elif game_state == GameStates.LEVEL_UP:
        level_up_menu(con, 'Level up! Choose a stat to raise:', player, 40, constants)
    elif game_state == GameStates.CHARACTER_SCREEN:
        character_screen(player, 30, 10, constants)

def clear_all(con, entities, game_map):
    for entity in entities:
        clear_entity(con, entity, game_map)


def draw_entity(con, entity, fov_map, game_map):
    if ((tcod.map_is_in_fov(fov_map, entity.x, entity.y) or (entity.stairs and game_map.tiles[entity.x][entity.y].explored)) and
        entity.x > game_map.view_x_min and entity.x < game_map.view_x_max and entity.y > game_map.view_y_min and entity.y < game_map.view_y_max):
        tcod.console_set_default_foreground(con, entity.color)
        tcod.console_put_char(con, entity.x - game_map.view_x_min, entity.y - game_map.view_y_min, entity.char, tcod.BKGND_NONE)


def clear_entity(con, entity, game_map):
    # erase the character that represents this object
    tcod.console_put_char(con, entity.x - game_map.view_x_min, entity.y - game_map.view_y_min, ' ', tcod.BKGND_NONE)