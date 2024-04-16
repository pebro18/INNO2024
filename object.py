import pygame


class Object:
    def __init__(self, x: int, y: int, size: int, visible: bool) -> None:
        self.x = x
        self.y = y
        self.size = size
        self.visible = visible

    def draw(self, screen: pygame.surface.Surface, image) -> None:
        if self.visible is True:
            screen.blit(source=pygame.transform.scale(image, (30, 30)), dest=(self.x - 15, self.y - 15))