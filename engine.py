import tcod

from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from input_handlers import handle_keys, handle_mouse, handle_main_menu
from loader_functions.initialize_new_game import get_game_variables
from loader_functions.data_loaders import load_game, save_game
from menus import main_menu, message_box
from render_functions import clear_all, render_all
from fov_functions import initialize_fov, recompute_fov
from game_messages import Message
from game_states import GameStates
from config import get_constants

constants = get_constants()

def main():

    tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)

    tcod.console_init_root(constants.screen_width, constants.screen_height, constants.window_title, False)

    con = tcod.console_new(constants.screen_width, constants.screen_height)
    panel = tcod.console_new(constants.screen_width, constants.panel_height)

    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = tcod.image_load('menu_background.png')

    key = tcod.Key()
    mouse = tcod.Mouse()

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            main_menu(con, main_menu_background_image)

            if show_load_error_message:
                message_box(con, 'No save game to load', 50)

            tcod.console_flush()

            action = handle_main_menu(key)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
            elif new_game:
                player, entities, game_map, message_log, game_state = get_game_variables()
                game_state = GameStates.PLAYERS_TURN
                show_main_menu = False
            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif exit_game:
                break
        else:
            tcod.console_clear(con)
            play_game(player, entities, game_map, message_log, game_state, con, panel)

            show_main_menu = True

def play_game(player, entities, game_map, message_log, game_state, con, panel):

    player.fighter.ignore_damage = constants.ignore_damage

    fov_recompute = True

    fov_map = initialize_fov(game_map)

    key = tcod.Key()
    mouse = tcod.Mouse()

    previous_game_state = game_state

    targeting_item = None
    player_running = None

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, constants.fov_radius, constants.fov_light_walls, constants.fov_algorithm)
        render_all(con, panel, mouse, entities, player, game_map, fov_map, fov_recompute, message_log, game_state)
        fov_recompute = False
        tcod.console_flush()

        clear_all(con, entities, game_map)

        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        move = action.get('move')
        wait = action.get('wait')
        run = action.get('run')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        take_stairs = action.get('take_stairs')
        level_up = action.get('level_up')
        show_character_screen = action.get('show_character_screen')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        player_turn_results = []

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            dest_x = player.x + dx
            dest_y = player.y + dy

            if not game_map.is_blocked(dest_x,dest_y) or constants.no_clipping:
                target = get_blocking_entities_at_location(entities, dest_x, dest_y)

                if target:
                    player_turn_results.extend(player.fighter.attack(target))
                else:
                    player.move(dx, dy)
                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

        elif wait:
            game_state = GameStates.ENEMY_TURN
            
        elif pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)
                    break
            else:
                message_log.add_message(Message('There is nothing here to pick up.', tcod.yellow))

        if run and game_state == GameStates.PLAYERS_TURN:
            message_log.add_message(Message('Which direction do you want to run?', tcod.yellow))
            previous_game_state = game_state
            game_state = GameStates.CHARACTER_RUN

        if game_state.CHARACTER_RUN:
            dir = action.get('dir')
            if dir:
                # Try to move the first step in the run
                dx, dy = dir
                dest_x = player.x + dx
                dest_y = player.y + dy

                if game_map.is_blocked(dest_x,dest_y) or get_blocking_entities_at_location(entities, dest_x, dest_y):
                    # If blocked, put up message and return to previous game state
                    message_log.add_message(Message('You can\'t run in that direction!', tcod.yellow))
                    game_state = previous_game_state
                else:
                    # Set the run direction and get the blocked state for adjacent orthogonal directons
                    player_running = dir
                    if dx == 0:
                        running_blocked_state = {(1, 0):game_map.is_blocked(player.x + 1,player.y), (-1, 0):game_map.is_blocked(player.x - 1 ,player.y)}
                    elif dy == 0:
                        running_blocked_state = {(0, 1):game_map.is_blocked(player.x,player.y + 1), (0, -1):game_map.is_blocked(player.x,player.y - 1)}
                    else:
                        running_blocked_state = {(dx, 0):game_map.is_blocked(player.x + dx,player.y), (0, dy):game_map.is_blocked(player.x,player.y + dy)}
                    # Check for tunnel mode
                    run_tunnel_mode = list(running_blocked_state.values())[0] or list(running_blocked_state.values())[1]
                    # Make the move
                    player.move(dx, dy)
                    fov_recompute = True

                    game_state = GameStates.ENEMY_TURN

        if player_running and game_state == GameStates.PLAYERS_TURN:
            if not run_tunnel_mode:
                # Run algo for non-tunnels
                # Check to see if the orthogonal blocked state has changed
                for dir in running_blocked_state.keys():
                    (dx, dy) = dir
                    if running_blocked_state.get(dir) != game_map.is_blocked(player.x + dx, player.y + dy):
                        player_running = None
                        break
                else:
                    # Check for fighter entities in the fov
                    for entity in entities:
                        if not entity is player and tcod.map_is_in_fov(fov_map, entity.x, entity.y) and entity.fighter:
                            player_running = None
                            break
                if player_running:
                    # If the running flag wasn't reset by the checks, try to move
                    dx, dy = player_running
                    dest_x = player.x + dx
                    dest_y = player.y + dy
                    if game_map.is_blocked(dest_x,dest_y) or get_blocking_entities_at_location(entities, dest_x, dest_y):
                        # Stop if blocked
                        player_running = None
                    else:
                        # Run the next step in that direction
                        player.move(dx, dy)
                        fov_recompute = True

                        game_state = GameStates.ENEMY_TURN
            else:
                # Tunnel mode
                for entity in entities:
                        if not entity is player and tcod.map_is_in_fov(fov_map, entity.x, entity.y) and entity.fighter:
                            player_running = None
                            break
                else:
                    # Check to see if the run direction is blocked first
                    dx, dy = player_running
                    dest_x = player.x + dx
                    dest_y = player.y + dy
                    if game_map.is_blocked(dest_x,dest_y) or get_blocking_entities_at_location(entities, dest_x, dest_y):
                        # If it's blocked, check the two running blocked state directions.  
                        # If only one is unblocked, change the run direction to that and set the new run direction
                        (dx, dy) = list(running_blocked_state.keys())[0]
                        dir1_blocked = game_map.is_blocked(player.x + dx, player.y + dy)
                        (dx, dy) = list(running_blocked_state.keys())[1]
                        dir2_blocked = game_map.is_blocked(player.x + dx, player.y + dy)
                        if dir1_blocked ^ dir2_blocked:
                            if dir1_blocked:
                                player_running = list(running_blocked_state.keys())[1]
                            else:
                                player_running = list(running_blocked_state.keys())[0]
                            # Update the blocking map, setting the expectation to false for both directions
                            (dx, dy) = player_running
                            if dx == 0:
                                running_blocked_state = {(1, 0):True, (-1, 0):True}
                            elif dy == 0:
                                running_blocked_state = {(0, 1):True, (0, -1):True}
                            # Run the next step in that direction
                            player.move(dx, dy)
                            fov_recompute = True

                            game_state = GameStates.ENEMY_TURN

                        else:
                            # Stop running if both directions are unblocked
                            player_running = None
                    else:
                        # Run the next step normally if the blocking state for the directions hasn't changed
                        for dir in running_blocked_state.keys():
                            (dx, dy) = dir
                            if running_blocked_state.get(dir) != game_map.is_blocked(player.x + dx, player.y + dy):
                                player_running = None
                                break
                        else:
                            dx, dy = player_running
                            dest_x = player.x + dx
                            dest_y = player.y + dy
                            player.move(dx, dy)
                            fov_recompute = True

                            game_state = GameStates.ENEMY_TURN


        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
            item = player.inventory.items[inventory_index]
            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if take_stairs and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.stairs and entity.x == player.x and entity.y == player.y:
                    entities = game_map.next_floor(player, message_log)
                    fov_map = initialize_fov(game_map)
                    fov_recompute = True
                    tcod.console_clear(con)

                    break
            
            else:
                message_log.add_message(Message('There are no stairs here.', tcod.yellow))
        
        if level_up:
            if level_up == 'hp':
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            elif level_up == 'str':
                player.fighter.base_power += 1
            elif level_up == 'def':
                player.fighter.base_defense += 1

            game_state = previous_game_state

        if show_character_screen:
            game_state = previous_game_state
            game_state = GameStates.CHARACTER_SCREEN

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click
                item_use_results = player.inventory.use(targeting_item, entities = entities, fov_map = fov_map, target_x = target_x+game_map.view_x_min, target_y = target_y+game_map.view_y_min)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN, GameStates.CHARACTER_RUN):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                save_game(player, entities, game_map, message_log, game_state)
                return True
        
        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_used = player_turn_result.get('item_used')
            item_dropped = player_turn_result.get('item_dropped')
            equip = player_turn_result.get('equip')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')
            xp = player_turn_result.get('xp')

            if message:
                 message_log.add_message(message)

            if targeting_cancelled:
                game_state = previous_game_state
                message_log.add_message(Message('Targeting cancelled'))

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)

                game_state = GameStates.ENEMY_TURN

            if item_consumed or item_used:
                game_state = GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

            if item_dropped:
                entities.append(item_dropped)

                game_state = GameStates.ENEMY_TURN

            if equip:
                equip_results = player.equipment.toggle_equip(equip)

                for equip_result in equip_results:
                    equipped = equip_result.get('equipped')
                    dequipped = equip_result.get('dequipped')

                    if equipped:
                        message_log.add_message(Message(f'You equipped the {equipped.name}'))

                    if dequipped:
                        message_log.add_message(Message(f'You dequipped the {dequipped.name}'))

            if xp:
                leveled_up = player.level.add_xp(xp)
                message_log.add_message(Message(f'You gain {xp} experience points.'))

                if leveled_up:
                    message_log.add_message(Message(f'Your battle skills grow stronger! You have reached {player.level.current_level}!', tcod.yellow))
                    previous_game_state = game_state
                    game_state = GameStates.LEVEL_UP


        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)
                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                             message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break
                    if game_state == GameStates.PLAYER_DEAD:
                        break

            else:
                game_state = GameStates.PLAYERS_TURN

        

if __name__ == '__main__':
    main()