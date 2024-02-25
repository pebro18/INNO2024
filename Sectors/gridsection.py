import pygame

class Grid():
    def __init__(self, name, x, y, cellsize):
        self.name = name
        self.x = x
        self.y = y
        self.radius = cellsize
        self.food_in_list = []
        self.weapons_in_list = []
        self.agent_list = []


        self.image = pygame.Surface([2, 2])
        self.image.fill((255, 255, 255))

        self.rect = self.image.get_rect()
        self.rect.x = self.x + 15
        self.rect.y = self.y + 15
    
    def add_food(self, food):
        self.food_in_list.append(food)

    def add_weapon(self, weapon):
        self.weapons_in_list.append(weapon)

    def add_agent(self, agent):
        self.agent_list.append(agent)

    def remove_food(self, food):
        self.food_in_list.remove(food)

    def remove_weapon(self, weapon):
        self.weapons_in_list.remove(weapon)

    def remove_agent(self, agent):
        self.agent_list.remove(agent)

    def get_food(self):
        return self.food_in_list
    
    def get_weapons(self):
        return self.weapons_in_list
    
    def get_agents(self):
        return self.agent_list
    
    def get_name(self):
        return self.name
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        pass
    
