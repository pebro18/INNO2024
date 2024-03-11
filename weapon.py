import pygame
from object import Object
from agents.player import Player


class Weapon(Object):
    def __init__(self, x: int, y: int, size: int, color: (int, int, int), visible: bool, damage: int) -> None:
        super().__init__(x, y, size, color, visible)
        self.damage = damage
        self.size = size

    def collision_detected(self, collisioned: Player) -> None:
        collisioned.weapon = self

    def draw(self, screen: pygame.surface.Surface) -> None:
        # Draw the handle
        handle_width = self.size // 2
        handle_x = self.x - handle_width // 2
        handle_y = self.y - self.size
        pygame.draw.rect(screen, self.color, (handle_x, handle_y, handle_width, handle_width + 10))

        # Draw the blade
        blade_width = self.size // 2
        blade_x = self.x - blade_width // 2
        blade_y = self.y - self.size
        pygame.draw.rect(screen, self.color, (blade_x, blade_y, blade_width + 10, blade_width))