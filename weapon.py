from object import Object
from player import Player


class Weapon(Object):
    def __init__(self, x: int, y: int, size: int, visible: bool, damage: int) -> None:
        super().__init__(x, y, size, visible)
        self.damage = damage
        self.size = size

    def collision_detected(self, collisioned: Player) -> None:
        collisioned.weapon = self