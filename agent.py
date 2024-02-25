import pygame
from Food.Food import FoodObj

class Agent(pygame.sprite.Sprite):
    """This Agent class represents a simple agent that can move around in the environment"""

    def __init__(self, start_position: pygame.math.Vector2):
        # Call the parent's constructor
        super().__init__()

        # Set height, width
        self.image = pygame.Surface([20, 20])
        self.image.fill((0, 255, 0))

        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.x = start_position[0] + 15
        self.rect.y = start_position[1] + 15

        # Set up attributes
        self.maxhunger = 50
        self.hunger = 50

        self.health = 100
        self.strength = 10
        self.hunger_rate = 1

        # Set up inventory
        self.weapon = None
        self.food = None

    def manual_move(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.rect.y -= 50
            if event.key == pygame.K_a:
                self.rect.x -= 50
            if event.key == pygame.K_s:
                self.rect.y += 50
            if event.key == pygame.K_d:
                self.rect.x += 50

    def agent_logic(self, grid):
        
        pass

    def move(self, grid):

        pass

    def look_around(self, grid):
 
        pass

    def pick_up(self,grid_section):
        
        pass

    def drop(self,grid_section):
        pass

    def eat(self):
        self.hunger += self.food.use_food()
        pass

    def fight(self,other_agent):

        pass 

    def die(self):
        pass

    def lose_hunger(self):
        self.hunger -= self.hunger_rate
        pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)