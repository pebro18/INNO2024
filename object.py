import pygame


class Object:
    def __init__(self, x: int, y: int, size: int, color: (int, int, int), visible: bool) -> None:
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.visible = visible

    def draw(self, screen: pygame.surface.Surface) -> None:
        if self.visible is True:
            pygame.draw.circle(surface=screen, color=self.color, center=(self.x, self.y), radius=self.size)