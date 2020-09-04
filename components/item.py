import re

plurals = {'Scroll':"Scrolls", "Potion":"Potions"}
regex = re.compile("|".join(plurals.keys()))
def pluralize(text):
    return regex.sub(lambda m: plurals[re.escape(m.group(0))], text)

class Item:
    def __init__(self, use_function = None, targeting = False, targeting_message=None, charges=None, stackable=False, use_kwargs={}):
        self.use_function = use_function
        self.targeting = targeting
        self.targeting_message  = targeting_message
        self.charges = charges
        self.function_kwargs = use_kwargs
        self.stackable = stackable
        self.stacks = 1
        
    def update_display_name(self):
        if self.stackable:
            if self.stacks > 1:
                self.owner.display_name = f'{self.stacks} {pluralize(self.owner.name)}'
            else:
                self.owner.display_name = self.owner.name
        elif self.charges:
            self.owner.display_name = f'{self.owner.name} ({self.charges} charges)'
        else:
            self.owner.display_name = self.owner.name