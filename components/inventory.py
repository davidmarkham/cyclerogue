import tcod

from game_messages import Message

class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        results = []
        if item.item.stackable:
            for inv_item in self.items:
                if item.name == inv_item.name:
                    inv_item.item.stacks += item.item.stacks
                    inv_item.item.update_display_name()
                    results.append({
                        'item_added': item,
                        'message': Message(f'You pick up the {item.display_name}, you now have {inv_item.item.stacks}.', tcod.blue)
                    })
                    break
            else:
                if len(self.items) >= self.capacity:
                    results.append({
                        'item_added': None,
                        'message': Message('You cannot carry any more, your inventory is full', tcod.yellow)
                    })
                else:
                    results.append({
                        'item_added': item,
                        'message': Message(f'You pick up the {item.display_name}.', tcod.blue)
                    })
                    self.items.append(item)
        else:
            if len(self.items) >= self.capacity:
                results.append({
                    'item_added': None,
                    'message': Message('You cannot carry any more, your inventory is full', tcod.yellow)
                })
            else:
                results.append({
                    'item_added': item,
                    'message': Message(f'You pick up the {item.display_name}.', tcod.blue)
                })
                self.items.append(item)

        return results

    def use(self, item_entity, **kwargs):
        results = []

        item_component = item_entity.item

        if item_component.use_function is None:
            equippable_component = item_entity.equippable

            if equippable_component:
                results.append({'equip': item_entity})
            else:
                results.append({'message': Message(f'The {item_entity.name} cannot be used', tcod.yellow)})
        else:
            if item_component.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                results.append({'targeting': item_entity})
            else:
                kwargs = {**item_component.function_kwargs, **kwargs}
                item_use_results = item_component.use_function(self.owner, item_entity, **kwargs)

                for item_use_result in item_use_results:
                    if item_use_result.get('consumed'):
                        if not item_component.stackable:
                            self.remove_item(item_entity)
                        elif item_component.stacks > 1:
                            item_component.stacks -= 1
                            item_component.update_display_name()
                            if item_component.stacks > 1:
                                results.append({'message': Message(f'You have {item_entity.display_name} left', tcod.yellow)})
                            else:
                                results.append({'message': Message(f'You have one {item_entity.display_name} left', tcod.yellow)})
                        else:
                            self.remove_item(item_entity)
                    if item_use_result.get('charge_used'):
                        item_component.charges -= 1
                        item_entity.item.update_display_name()
                
                results.extend(item_use_results)

        return results

    def remove_item(self, item):
        self.items.remove(item)

    def drop_item(self, item):
        results = []

        if self.owner.equipment.main_hand == item or self.owner.equipment.off_hand == item:
            self.owner.equipment.toggle_equip(item)

        item.x = self.owner.x
        item.y = self.owner.y

        self.remove_item(item)
        results.append({'item_dropped': item, 'message':Message(f'You dropped the {item.display_name}', tcod.yellow)})

        return results