import tcod

from random import randint

from game_messages import Message

class BasicMonster:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        monster = self.owner
        if self.kwargs.get('on_turn'):
            for func in self.kwargs.get('on_turn'):
                results.extend(func(monster, self.kwargs.get('function_params'), entities, game_map, fov_map))
        if tcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)
            elif target.fighter.hp > 0:
                results.extend(monster.fighter.attack(target))
        
        return results

class SmartMonster:
    def __init__(self, *args, **kwargs):
        self.target_x = None
        self.target_y = None
        self.args = args
        self.kwargs = kwargs

    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        monster = self.owner
        if self.kwargs.get('on_turn'):
            for func in self.kwargs.get('on_turn'):
                results.extend(func(monster, self.kwargs.get('function_params'), entities, game_map, fov_map))
        if tcod.map_is_in_fov(fov_map, monster.x, monster.y):
            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)
                self.target_x = target.x
                self.target_y = target.y
            elif target.fighter.hp > 0:
                results.extend(monster.fighter.attack(target))
        elif self.target_x != None and self.target_y != None:
            monster.move_astar_to_coords(self.target_x, self.target_y, entities, game_map)
            if self.owner.x == self.target_x and self.owner.y == self.target_y:
                self.target_x = None
                self.target_y = None
        return results
            
class ConfusedMonster:
    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def take_turn(self, target, fov_map, game_map, entities):
        results = []
        
        if self.previous_ai.kwargs.get('on_turn'):
            for func in self.previous_ai.kwargs.get('on_turn'):
                results.extend(func(self.owner, self.previous_ai.kwargs.get('function_params'), entities, game_map, fov_map))
        if self.number_of_turns > 0:
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                self.owner.move_towards(random_x, random_y, game_map, entities)

            self.number_of_turns -= 1

        else:
            self.owner.ai = self.previous_ai
            results.append({'message': Message(f'The {self.owner.name} is no longer confused!', tcod.red)})

        return results