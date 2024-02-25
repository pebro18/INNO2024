from Food import food
from Weapons import Weapons, WeaponsTypes
import random


class ObjectSpawner:
    """This class is responsible for spawning food and weapons in the game"""

    def __init__(self):
        self.food_list = []
        self.weapons_list = []

    def get_food_randomly(self):
        pass

    def get_weapons_randomly(self):
        

        pass

    def get_specific_food(self, name):
        return self.food_list[name]

    def get_specific_weapon(self, name):
        return self.weapons_list[name]

    """Define food and weapons in the game here and add them to the list
    so that they can be used by the spawn functions
    
    Example:
    self.define_food("Apple", 10, 10)
    self.define_weapons("Pistol", 10, 10, WeaponsTypes.PISTOL)
    """
    def define_food(self, name:str, food_points, quantity):
        self.food_list.append(food(name, food_points, quantity))
        pass

    def define_weapons(self, name: str, damage: int, ammo: int, type: WeaponsTypes):
        self.weapons_list.append(Weapons(name, damage, ammo, type))
