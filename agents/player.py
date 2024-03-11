import pygame
import random
from food import Food
from agents.enemy import Enemy


class Player:
    def __init__(self, x, y, radius, color, speed, max_hunger, max_health):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
        self.hunger = max_hunger
        self.max_hunger = max_hunger
        self.damage = 2
        self.weapon = None
        self.max_health = max_health
        self.health = max_health
        self.not_food = {}
        self.map_has_visited = [[]]
        self.memory = {}
        self.direction = None
        self.amount_of_steps = 0

        self.hotspot = None
        self.map_enemy_grid_probabilities = []

    def index(self) -> (int, int):
        """
        Get the current position of the agent based on coordinates
        :return: Tuple (int, int): x and y coordinates of agent
        """
        return self.x // self.speed, self.y // self.speed

    def add_grids(self, x, y) -> [(int, int)]:
        """

        :param x:
        :param y:
        :return:
        """
        min, max = 0, 19

        lst = []
        if min < x < max:
            lst += [(x + 1, y), (x - 1, y)]
        elif x == min:
            lst += [(x + 1, y)]
        elif x == max:
            lst += [(x - 1, y)]

        return lst

    def get_adjacent_tiles(self, tiles) -> []:
        """
        Get the Agent's adjecent tiles
        :param tiles: The entire Grid
        :return: a list with all adjecent tiles
        """
        x, y = self.index()  # Current position
        return [tiles[x][y] for x, y in self.add_grids(x, y) + [coords[::-1] for coords in self.add_grids(y, x)]]

    def move(self, dx, dy, tiles):
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
        if (0 < new_x < bottom_right_tile.x + bottom_right_tile.size) and (0 < new_y < bottom_right_tile.y + bottom_right_tile.size):
            self.x = new_x  # Set new x-coordinate
            self.y = new_y  # Set new y-coordinate
        x, y = self.index()
        tiles[x][y].color = (122, 122, 122)

    def go_to_tile(self, tile, tiles):
        """
        Calculates what the next x- and y-coordinates are
        :param tile: Next tile
        :param tiles: The entire Grid
        :return:
        """
        tile_x, tile_y = tile.index()
        print(f'{self.index()}\t({tile_x}, {tile_y})')
        x, y = self.index()
        new_x = 1 if tile_x - x > 0 else (-1 if tile_x - x < 0 else 0)
        if new_x != 0:  # If the next x-coordinate is not the same:
            self.move(new_x, 0, tiles)
        else:  # Move Agent on y-axis
            new_y = 1 if tile_y - y > 0 else (-1 if tile_y - y < 0 else 0)
            self.move(0, new_y, tiles)

    def move_direction(self, tiles):
        """
        Move the agent to a direction
        :param tiles:
        :return:
        """
        self.amount_of_steps -= 1

        # Check if enemy is in adjacent tiles and if so, move away from it
        # Reactive behaviour
        enemy_dectected = self.enemy_detected(tiles)
        if enemy_dectected != None:
            self.direction = enemy_dectected

        if self.direction == "north":
            self.move(0, -1, tiles)
        elif self.direction == "east":
            self.move(1, 0, tiles)
        elif self.direction == "south":
            self.move(0, 1, tiles)
        elif self.direction == "west":
            self.move(-1, 0, tiles)

    def detect_food(self, tiles):
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
                    # print("Found food!")
        # print(food_dict)
        return food_dict

    def max_food_probability(self, tiles, update_probability):
        """
        Calculate the probability of finding food
        :param tiles: The entire Grid
        :param update_probability: Boolean if the probability has to be updated
        :return: tile where the highest chance is of finding food
        """
        food_tiles = {}
        for timestep in self.memory:
            tile, objects = self.memory[timestep]
            if Food in objects:
                food_tiles[tile] = food_tiles.get(tile, 0) + 1

        if update_probability is True:  # If the probability has to be updated:
            for tile in self.get_adjacent_tiles(tiles):
                for timestep in self.memory:
                    tile_memory, objects = self.memory[timestep]
                    if tile == tile_memory and Food not in [type(object) for object in tile.objects]:
                        self.not_food[tile] = self.not_food.get(tile, 0) + 1

        for tile in food_tiles:
            food_tiles[tile] /= food_tiles[tile] + self.not_food.get(tile, 0)
        try:
            maximum = max(food_tiles, key=lambda x: food_tiles[x])
        except ValueError:
            return None

        self.notFoundFood = []

        if self.index() == maximum.index() and Food not in [type(object) for object in maximum.objects]:
            return None
        else:
            return maximum

    def reset_map(self, tiles):
        """
        Reset the map
        :param tiles: The entire Grid
        :return: None
        """
        new_map = []
        for tile in tiles:  # For every tile in the grid
            new = []
            for num_tile in range(len(tiles)):
                new.append(0)
            new_map.append(new)
        self.map_has_visited = new_map
        self.map_food_probability = new_map
        self.map_enemy_grid_probabilities = new_map

    def update_memory(self, timestep, tiles):
        """
        Update the Agent's memory
        :param timestep: Current tick
        :param tiles: The entire Grid
        :return: None
        """
        x, y = self.index()
        tuple = (tiles[x][y], tiles[x][y].objects)
        if tuple[1]:
            lst = []
            for object in tuple[1]:
                lst.append(type(object))
            self.memory[timestep] = (tuple[0], lst)

    def choose_direction(self, tiles, amount_tiles):
        """
        Look at all directions and determine how many tiles are not explored yet. Decide based on this which direction to go to.
        :param tiles: The entire grid
        :param amount_tiles: Amount of tiles the Agent can see ahead of him
        :return: Direction with the most amount of tiles that aren't explored yet
        """
        directions = {"north": 0, "east": 0, "south": 0, "west": 0}
        latest_direction = None
        directions = self.enemy_avoidance_based_on_memory(directions, tiles, amount_tiles)
        x, y = self.index()
        for i in range(x - 1, max(x - amount_tiles - 1, -1), -1):  # Check west direction
            # if not tiles[i][y].objects:
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

    def enemy_avoidance_based_on_memory(self, directions, tiles, amount_tiles):
        """
        Look at all directions and determine how many times it saw an enemy in that direction.
        :param directions: All directions the Agent can move to
        :param tiles: The entire Grid
        :param amount_tiles: Amount of tiles it looks ahead
        :return: Dictionary with all directions and its score
        """
        x, y = self.index()
        rememberance_of_enemies = self.search_enemy_in_memory()
        enemy_positions = []
        for enemy in rememberance_of_enemies:
            indexed_x = enemy.x // (self.radius * 2)
            indexed_y = enemy.y // (self.radius * 2)
            enemy_positions.append((indexed_x, indexed_y))

        for i in range(x - 1, max(x - amount_tiles - 1, -1), -1):  # Check west direction
            if (i, y) in enemy_positions:
                directions["west"] -= 1

        for i in range(x + 1, min(x + amount_tiles + 1, len(tiles))):  # Check east direction
            if (i, y) in enemy_positions:
                directions["east"] -= 1

        for j in range(y - 1, max(y - amount_tiles - 1, -1), -1):  # Check north direction
            if (x, j) in enemy_positions:
                directions["north"] -= 1

        for j in range(y + 1, min(y + amount_tiles + 1, len(tiles[0]))):  # Check south direction
            if (x, j) in enemy_positions:
                directions["south"] -= 1
        return directions

    def calculate_enemy_prob_of_entire_grid_based_on_memory(self, tiles):
        """
        Calculate the probability of encountering an enemy based on how many encounters it has had in its memory
        :param tiles: The entire Grid
        :return: None
        """
        enemy_positions = []
        rememberance_of_enemies = self.search_enemy_in_memory()

        for enemy in rememberance_of_enemies:
            indexed_x = enemy.x // (self.radius * 2)
            indexed_y = enemy.y // (self.radius * 2)
            enemy_positions.append((indexed_x, indexed_y))

        for i in range(len(self.map_enemy_grid_probabilities)):
            for j in range(len(self.map_enemy_grid_probabilities[i])):
                if (i, j) in enemy_positions:
                    print("enemy detected in grid position: ", i, j, "")
                    self.map_enemy_grid_probabilities[i][j] += 1
                else:
                    self.map_enemy_grid_probabilities[i][j] = 0
        pass

    def search_enemy_in_memory(self):
        """
        Look for enemies that have been encountered in its memory
        :return: List of all enemies that have been enountered
        """
        list_of_enemies = []
        for key, value in self.memory.items():
            for obj in value[1]:
                if isinstance(obj, Enemy):
                    list_of_enemies.append(obj)
        return list_of_enemies

    def enemy_detected(self, tiles):
        """
        Detect where an enemy is
        :param tiles: The entire Grid
        :return: String of the direction that an enemy has been detected
        """
        x, y = self.index()  # Current position
        get_tiles_data = self.get_adjacent_tiles(tiles)  # Get adjecent tiles

        for tile in get_tiles_data:
            if len(tile.objects) > 0:  # If there is an object in the tile
                for obj in tile.objects:  # For each object in the tile
                    if isinstance(obj, Enemy):  # if the object is an enemy
                        indexed_x = tile.x // (self.radius * 2)  # x-coordinate of enemy
                        indexed_y = tile.y // (self.radius * 2)  # y-coordinate of enemy
                        if indexed_x < x:
                            return "east"
                        elif indexed_x > x:
                            return "west"
                        elif indexed_y < y:
                            return "south"
                        elif indexed_y > y:
                            return "north"
        return None

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

    def remember_attack(self, enemy, timestamp):
        # self.memory[timestamp] += enemy
        pass