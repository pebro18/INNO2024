import pygame


class Tile:
    def __init__(self, x: int, y: int, size: int, color: (int, int, int)) -> None:
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.objects = []

    def index(self) -> (int, int):
        return self.x // self.size, self.y // self.size

    def draw(self, screen: pygame.surface.Surface) -> None:
        rect = pygame.Rect(self.x, self.y, self.size, self.size)
        rect.center = (self.x, self.y)
        pygame.draw.rect(surface=screen, color=self.color, rect=rect)
        pygame.draw.rect(surface=screen, color=(0, 0, 0), rect=rect, width=1)