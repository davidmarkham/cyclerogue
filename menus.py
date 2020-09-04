import tcod


def menu(con, header, options, width, constants):
    if len(options) > 26: 
        raise ValueError('Cannot have a menu with more than 26 options.')

    # Calculate total height for the header after auto-wrap and one line per option
    header_height = tcod.console_get_height_rect(con, 0, 0, width, constants.screen_height, header)
    height = len(options) + header_height

    # Create an off-screen console that represents the menu's window
    window = tcod.console_new(width, height)

    # Print the header, with auto-wrap
    tcod.console_set_default_foreground(window, tcod.white)
    tcod.console_print_rect_ex(window, 0, 0, width, height, tcod.BKGND_NONE, tcod.LEFT, header)

    # Print the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ')' + option_text
        tcod.console_print_ex(window, 0, y, tcod.BKGND_NONE, tcod.LEFT, text)
        y += 1
        letter_index += 1

    # Blit the contents of "window" to the root console
    x = int(constants.screen_width / 2 - width / 2)
    y = int(constants.screen_height / 2 - height / 2)
    tcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    
def inventory_menu(con, header, player, inventory_width, constants):
    # Shows a menu with each item of the inventory as an option
    if len(player.inventory.items) == 0:
        options = ['Inventory is empty.']
    else:
        options = []

        for item in player.inventory.items:
            if player.equipment.main_hand == item:
                options.append(f'{item.display_name} (on main hand)')
            elif player.equipment.off_hand == item:
                options.append(f'{item.display_name} (on off hand)')
            else:
                options.append(item.display_name)


    menu(con, header, options, inventory_width, constants)


def main_menu(con, background_image, constants):
    tcod.image_blit_2x(background_image, 0, 0, 0)

    tcod.console_set_default_foreground(0, tcod.dark_red)
    tcod.console_print_ex(0, int(constants.screen_width / 2), int(constants.screen_height / 2) - 4, tcod.BKGND_NONE, tcod.CENTER, 'CycleRogue')
    tcod.console_print_ex(0, int(constants.screen_width / 2), int(constants.screen_height - 2), tcod.BKGND_NONE, tcod.CENTER, 'By David Markham')

    menu(con, '', ['Play a new game', 'Continue last game', 'Quit'], 24, constants)

def level_up_menu(con, header, player, menu_width, constants):
    options = [f'Constitution (+20 Max HP, from {player.fighter.max_hp}',
               f'Strength (+1 attack, from {player.fighter.power}',
               f'Agility (+1 defense, from {player.fighter.defense}']

    menu(con, header, options, menu_width, constants)

def character_screen(player, character_screen_width, character_screen_height, constants):
    window = tcod.console_new(character_screen_width, character_screen_height)

    tcod.console_set_default_foreground(window, tcod.white)

    tcod.console_print_rect_ex(window, 0, 1, character_screen_width, character_screen_height, tcod.BKGND_NONE, tcod.LEFT, 'Character Information')
    tcod.console_print_rect_ex(window, 0, 2, character_screen_width, character_screen_height, tcod.BKGND_NONE, tcod.LEFT, f'Level: {player.level.current_level}')
    tcod.console_print_rect_ex(window, 0, 3, character_screen_width, character_screen_height, tcod.BKGND_NONE, tcod.LEFT, f'Experience {player.level.current_xp}')
    tcod.console_print_rect_ex(window, 0, 4, character_screen_width, character_screen_height, tcod.BKGND_NONE, tcod.LEFT, f'Experience to Next Level: {player.level.experience_to_next_level}')
    tcod.console_print_rect_ex(window, 0, 6, character_screen_width, character_screen_height, tcod.BKGND_NONE, tcod.LEFT, f'Maximum HP: {player.fighter.base_max_hp}+{player.equipment.max_hp_bonus}')
    tcod.console_print_rect_ex(window, 0, 7, character_screen_width, character_screen_height, tcod.BKGND_NONE, tcod.LEFT, f'Attack: {player.fighter.base_power}+{player.equipment.power_bonus}')
    tcod.console_print_rect_ex(window, 0, 8, character_screen_width, character_screen_height, tcod.BKGND_NONE, tcod.LEFT, f'Defense: {player.fighter.base_defense}+{player.equipment.defense_bonus}')

    x = constants.screen_width // 2 - character_screen_width // 2
    y = constants.screen_height // 2 - character_screen_height // 2
    tcod.console_blit(window, 0, 0, character_screen_width, character_screen_height, 0, x, y, 1.0, 0.7)
    

def message_box(con, header, width, constants):
    menu(con, header, [], width, constants)