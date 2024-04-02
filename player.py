import pygame
import random
from food import Food
from tile import Tile


class Player:
    def __init__(self, x: int, y: int, radius, color, speed, max_hunger, max_health) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
        self.hunger = max_hunger
        self.max_hunger = max_hunger
        self.max_health = max_health

        self.health = max_health
        self.weapon = None
        self.damage = 2

        self.not_food = {}
        self.map_has_visited = [[]]
        self.memory = {}
        self.direction = None
        self.amount_of_steps = 0
        self.hotspot = None

        self.has_visited = []

    def __str__(self) -> str:
        return f'Player at {self.index()}'

    def update_behaviour(self, tiles, timestep):
        action = self.choose_action(tiles)  # Kies een actie
        self.perform_action(action, tiles)  # Voer de gekozen actie uit

        self.update_memory(timestep, tiles)  # Update memory
        self.update_hunger(-1)  # Verander honger met -1

    def choose_action(self, tiles):
        """ Return Possible Actions: [Random Move, Go To Highest Food Probability]"""
        if self.hunger > self.max_hunger / 2:  # Beweeg random als de agent boven max_hunger / 2 is
            return "Random Move"
        elif self.hunger <= self.max_hunger / 2:  # Ga naar voedsel met hoogste kans op voedsel
            probabilities = self.calculate_food_probabilities(tiles, False)
            for tile, probability in probabilities.items():
                if tile not in self.has_visited:
                    return "Go To Highest Food Probability"
            return "Random Move"  # Als er geen tiles zijn, dan random move

    def perform_action(self, action, tiles):
        if action == "Random Move":
            self.random_move(tiles, tiles[0][0].size)
        elif action == "Go To Highest Food Probability":
            self.go_to_highest_food_probability(tiles)

    def go_to_highest_food_probability(self, tiles):
        probabilities = self.calculate_food_probabilities(tiles, False)

        detected_food = self.detect_food(tiles)  # Check if the player finds food, else this variable is None
        if detected_food:  # If the player found food
            goal = max(detected_food, key=lambda k: detected_food[k])  # Target tile for the agent
            self.move((goal.x + 15 - (self.x + 15)) // (self.radius * 2), (goal.y + 15 - (self.y + 15)) // (self.radius * 2), tiles)  # Move the player closer to the tile
        else:
            for tile, probability in probabilities.items():  # Ga naar tile waar hij nog niet is geweest.
                if tile.index() == self.index() and tile not in self.has_visited:  # Als de player op een tile zit in de lijst, voeg hem dan aan de lijst
                    self.has_visited.append(tile)
                elif tile not in self.has_visited:
                    self.go_to_tile(tile, tiles)
                    break

    def index(self) -> (int, int):
        """
        Get the current position of the agent based on coordinates
        :return: Tuple (int, int): x and y coordinates of agent
        """
        return self.x // self.speed, self.y // self.speed

    def add_grids(self, x: int, y: int, minimum=0, maximum=19) -> [(int, int)]:
        """
        Get the indexes of the possible grids
        :param x: int
        :param y: int
        :param minimum: int
        :param maximum: int
        :return: List of Tuples (int, int): x and y index of grid
        """
        lst = []
        if minimum < x < maximum:
            lst += [(x + 1, y), (x - 1, y)]
        elif x == minimum:
            lst += [(x + 1, y)]
        elif x == maximum:
            lst += [(x - 1, y)]
        return lst

    def get_adjacent_tiles(self, tiles: [[Tile]]) -> [Tile]:
        """
        Get the Agent's adjacent tiles
        :param tiles: The entire Grid
        :return: A list with all adjacent tiles
        """
        x, y = self.index()  # Current position
        return [tiles[x][y] for x, y in self.add_grids(x=x, y=y) + [coords[::-1] for coords in self.add_grids(x=y, y=x)]]

    def move(self, dx: int, dy: int, tiles: [[Tile]]) -> None:
        """
        Set the next x- and y-coordinates for the Agent
        :param dx: Difference in x
        :param dy: Difference in y
        :param tiles: The entire Grid
        :return: None
        """
        x, y = self.index()
        self.map_has_visited[x][y] = 1

        new_x = self.x + dx * self.speed  # Next x-coordinate
        new_y = self.y + dy * self.speed  # Next y-coordinate
        bottom_right_tile = tiles[-1][-1]
        if (0 < new_x < bottom_right_tile.x + bottom_right_tile.size) and (
                0 < new_y < bottom_right_tile.y + bottom_right_tile.size):
            self.x = new_x  # Set new x-coordinate
            self.y = new_y  # Set new y-coordinate
            tiles[x][y].objects.remove(self)
            tiles[new_x // self.speed][new_y // self.speed].append(self)

    def go_to_tile(self, tile: Tile, tiles: [[Tile]]) -> None:
        """
        Calculates what the next x- and y-coordinates are
        :param tile: Next tile
        :param tiles: The entire Grid
        :return: None
        """
        tile_x, tile_y = tile.index()
        x, y = self.index()
        new_x = 1 if tile_x - x > 0 else (-1 if tile_x - x < 0 else 0)
        if new_x != 0:  # If the next x-coordinate is not the same:
            self.move(dx=new_x, dy=0, tiles=tiles)
        else:  # Move Agent on y-axis
            new_y = 1 if tile_y - y > 0 else (-1 if tile_y - y < 0 else 0)
            self.move(dx=0, dy=new_y, tiles=tiles)

    def move_direction(self, tiles: [[Tile]]) -> None:
        """
        Move the agent to a direction
        :param tiles: The entire Grid
        :return: None
        """
        self.amount_of_steps -= 1

        if self.direction == "north":
            self.move(0, -1, tiles)
        elif self.direction == "east":
            self.move(1, 0, tiles)
        elif self.direction == "south":
            self.move(0, 1, tiles)
        elif self.direction == "west":
            self.move(-1, 0, tiles)

    def detect_food(self, tiles: [[Tile]]) -> dict:
        """
        See if there is food in adjecent tiles
        :param tiles: The entire Grid
        :return: Dictionary of all foods in the adjecent tiles
        """
        food_dict = {}
        for tile in self.get_adjacent_tiles(tiles):
            for object in tile.objects:
                if isinstance(object, Food):
                    food_dict[tile] = food_dict.get(tile, 0) + 1
        return food_dict

    def calculate_food_probabilities(self, tiles: [[Tile]], update_probability: bool) -> dict:
        """
        Calculate the probability of finding food
        :param tiles: The entire Grid
        :param update_probability: Boolean if the probability has to be updated
        :return: Sorted dictionary of food probabilities
        """
        food_tiles = {}
        for timestep in self.memory:
            tile, objects = self.memory[timestep]
            if Food in objects:
                food_tiles[tile] = food_tiles.get(tile, 0) + 1

        if update_probability:  # If the probability has to be updated:
            for tile in self.get_adjacent_tiles(tiles=tiles):
                for timestep in self.memory:
                    tile_memory, objects = self.memory[timestep]
                    if tile == tile_memory and Food not in [type(object) for object in tile.objects]:
                        self.not_food[tile] = self.not_food.get(tile, 0) + 1

        for tile in food_tiles:
            food_tiles[tile] /= food_tiles[tile] + self.not_food.get(tile, 0)

        return dict(reversed(sorted(food_tiles.items(), key=lambda item: item[1])))

    def reset_map(self, tiles: [[Tile]]) -> None:
        """
        Reset the map
        :param tiles: The entire Grid
        :return: None
        """
        self.map_has_visited = [[0 for num_tile in range(len(tiles))] for tile in tiles]

    def update_memory(self, timestep: int, tiles: [[Tile]]) -> None:
        """
        Update the Agent's memory
        :param timestep: Current tick
        :param tiles: The entire Grid
        :return: None
        """
        x, y = self.index()
        tile, objects = (tiles[x][y], tiles[x][y].objects)
        if objects:
            self.memory[timestep] = (tile, [type(object) for object in objects])

    def choose_direction(self, tiles: [[Tile]], amount_tiles: int) -> str:
        """
        Look at all directions and determine how many tiles are not explored yet.
        Decide based on this which direction to go to.
        :param tiles: The entire grid
        :param amount_tiles: Amount of tiles the Agent can see ahead of him
        :return: Direction with the most amount of tiles that aren't explored yet
        """
        directions = {"north": 0, "east": 0, "south": 0, "west": 0}
        x, y = self.index()
        for i in range(x - 1, max(x - amount_tiles - 1, -1), -1):  # Check west direction
            if self.map_has_visited[i][y] == 0:
                directions["west"] += 1
        for i in range(x + 1, min(x + amount_tiles + 1, len(tiles))):  # Check east direction
            if self.map_has_visited[i][y] == 0:
                directions["east"] += 1
        for j in range(y - 1, max(y - amount_tiles - 1, -1), -1):  # Check north direction
            if self.map_has_visited[x][j] == 0:
                directions["north"] += 1
        for j in range(y + 1, min(y + amount_tiles + 1, len(tiles[0]))):  # Check south direction
            if self.map_has_visited[x][j] == 0:
                directions["south"] += 1

        return max(directions, key=directions.get)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        # Calculate the width and height of the hunger bar
        bar_width = self.radius * 2
        bar_height = 10

        # Calculate the position of the hunger bar
        bar_x = self.x - self.radius
        bar_y = self.y + self.radius + 5

        # Calculate the percentage of hunger remaining
        percent_remaining = self.hunger / self.max_hunger

        # Calculate the color of the hunger bar
        if percent_remaining > 0.5:
            bar_color = (0, 255, 0)
        elif percent_remaining > 0.25:
            bar_color = (255, 255, 0)
        else:
            bar_color = (255, 0, 0)

        # Draw the hunger bar
        pygame.draw.rect(screen, (128, 128, 128), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, bar_width * percent_remaining, bar_height))

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

    def update_hunger(self, amount: int):
        """
        Update Agent's hunger
        :param amount: The change in hunger
        :return: None
        """
        self.hunger += amount
        if self.hunger > self.max_hunger:
            self.hunger = self.max_hunger
        elif self.hunger < 0:
            self.hunger = 0

    def update_health(self, amount):
        """
        Update Agent's health
        :param amount: The change in health
        :return: None
        """
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
        elif self.health < 0:
            self.health = 0

    def use_weapon(self):
        """
        Use weapon if the agent has one
        :return:
        """
        if self.weapon is not None:  # If the agent has a weapon
            base_damage = self.damage + self.weapon.damage
        else:
            base_damage = self.damage
        return random.randint(base_damage - 2, base_damage + 2)

    def random_move(self, tiles: [[Tile]], TILE_SIZE) -> None:
        """
        Move the player to a random tile.
        :param tiles: The entire Grid
        :return: None
        """
        if self.amount_of_steps == 0:  # If the player is in its starting position
            self.direction = self.choose_direction(tiles, 3)
            self.amount_of_steps = 3  # Add amount of taken steps to agent
        detected_food = self.detect_food(tiles)  # Check if the player finds food, else this variable is None
        if detected_food:  # If the player found food
            goal = max(detected_food, key=lambda k: detected_food[k])  # Target tile for the agent
            self.move((goal.x + 15 - (self.x + 15)) // TILE_SIZE, (goal.y + 15 - (self.y + 15)) // TILE_SIZE,
                        tiles)  # Move the player closer to the tile
        else:
            self.move_direction(tiles)  # Move the player with different logic

    def collision_food(self, food: Food, tiles: [[Tile]]) -> bool:
        """
        Check for collisions with food object
        :param food: Food item
        :param tiles: The entire grid
        :return: boolean
        """
        distance = ((self.x - food.x) ** 2 + (self.y - food.y) ** 2) ** 0.5
        if distance < self.radius + food.size:
            food.collision_detected(self)
            x, y = self.index()
            tiles[x][y].objects.remove(food)
            self.has_visited = []
            return True
        return False

    def collision_weapon(self, weapon, tiles):
        """
        Check for collisions with weapons
        :param weapon: Weapon object
        :param tiles: The entire grid
        :return: None
        """
        distance = ((self.x - weapon.x) ** 2 + (self.y - weapon.y) ** 2) ** 0.5
        if distance < self.radius + weapon.size:
            weapon.collision_detected(self)
            x, y = self.index()
            tiles[x][y].objects.remove(weapon)
            return True
        return False

    def can_communicate(self, tiles: [[Tile]]) -> bool:
        x, y = self.index()
        for object in tiles[x][y].objects:
            if object != self and Player == type(object):
                return True
        for adjacent_tile in self.get_adjacent_tiles(tiles=tiles):
            for object in adjacent_tile.objects:
                if object != self and Player == type(object):
                    return True
        return False