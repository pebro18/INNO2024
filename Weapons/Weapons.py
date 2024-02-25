import WeaponsTypes

class Weapons:
    """Weapons class represents a weapon in the game. It has a name, damage, ammo, and type.
    Attributes:
        name (str): The name of the weapon.
        damage (int): The amount of damage the weapon does.
        ammo (int): The amount of ammo the weapon has. incase of melee weapons, this is set to 0. 
        type (WeaponsTypes): The type of the weapon. This is an enum of WeaponsTypes."""	
    def __init__(self, name: str, damage : int, ammo :int, type : WeaponsTypes):
        self.name = name
        self.damage = damage
        self.ammo = ammo
        self.type = type
    
    def slash(self):
        return self.damage

    def fire(self):
        if self.ammo > 0:
            self.ammo -= 1
            return self.damage
        else:
            return 0

    def __str__(self):
        return f"Name: {self.name}, Damage: {self.damage}, Ammo: {self.ammo}"

    def __repr__(self):
        return f"Name: {self.name}, Damage: {self.damage}, Ammo: {self.ammo}"