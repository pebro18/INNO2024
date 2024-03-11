import pygame
import random


class Enemy:
    def __init__(self, x, y, radius, color, speed, max_health, current_tile):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
        self.health = max_health
        self.max_health = max_health
        self.weapon = None
        self.damage = 2
        self.current_tile = current_tile
        current_tile.objects.append(self)

    def move(self, WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE, tiles):
        possible_movesets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random_move = random.choice(possible_movesets)
        new_x = self.x // TILE_SIZE + random_move[0]
        new_y = self.y // TILE_SIZE + random_move[1]

        if 0 < new_x < WINDOW_WIDTH // TILE_SIZE and 0 < new_y < WINDOW_HEIGHT // TILE_SIZE:
            self.current_tile.objects.remove(self)
            new_tile = tiles[new_x][new_y]
            self.x = new_tile.x
            self.y = new_tile.y
            new_tile.objects.append(self)
            self.current_tile = new_tile
        else:
            self.move(WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE, tiles)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

        # Calculate the width and height of the health bar
        bar_width = self.radius * 2
        bar_height = 5

        # Calculate the position of the health bar
        bar_x = self.x - self.radius
        bar_y = self.y - self.radius - 10

        # Calculate the percentage of health remaining
        percent_remaining = self.health / self.max_health

        # Calculate the color of the health bar
        if percent_remaining > 0.5:
            bar_color = (0, 255, 0)
        elif percent_remaining > 0.25:
            bar_color = (255, 255, 0)
        else:
            bar_color = (255, 0, 0)

        # Draw the health bar
        pygame.draw.rect(screen, (128, 128, 128), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, bar_width * percent_remaining, bar_height))

    def use_weapon(self):
        if self.weapon is not None:
            base_damage = self.damage + self.weapon.damage
        else:
            base_damage = self.damage
        return random.randint(base_damage - 2, base_damage + 2)