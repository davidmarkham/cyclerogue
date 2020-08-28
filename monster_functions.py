import tcod
from game_messages import Message

def regeneration(*args, **kwargs):
    results = [] 
    monster = args[0]
    if monster.fighter.hp < monster.fighter.max_hp:
        regen_rate = args[1].get('regen_rate')
        monster.fighter.heal(regen_rate)
        if tcod.map_is_in_fov(args[4], monster.x, monster.y):
            results.append({'message':Message(f'The {monster.name} regenerates for {regen_rate}!', tcod.light_green)})
    return resultsz