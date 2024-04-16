import pygame
import random
from food import Food
from tile import Tile
from coalition import Coalition
from typing import List, Tuple, Any


class Player:
    def __init__(self, x: int, y: int, radius: int, color: Tuple[int, int, int], speed: int, max_hunger: int,
                 max_health: int, agent_values: dict) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed
        self.max_hunger = max_hunger * (agent_values['Resourcefulness'] * 1.5)
        self.hunger = self.max_hunger
        self.max_health = max_health

        self.health = max_health
        self.weapon = None
        self.damage = 1

        self.not_food = {}
        self.map_has_visited = [[]]
        self.memory = {}
        self.direction = None
        self.amount_of_steps = 0
        self.has_visited = []

        self.agent_values = agent_values  # agent_values = {'Strength': 2, 'Resourcefulness': 2}
        self.coalition = None

    def __str__(self) -> str:
        return f'Player at {self.index()}'

    def empty_coalition(self, coalitions: List[Coalition]) -> Coalition:
        """
        Look for a empty coalition.

        :param coalitions: List of all coalitions
        :return: A empty coalition
        """
        for coalition in coalitions:
            if not coalition.members:
                return coalition

    def evaluate_coalition_with_individual(self, agent, coalitions: List[Coalition]) -> None:
        """
        Evalueer of een agent zich moet aansluiten bij een agent op basis van de waarde die de agent zou hebben binnen
        en buiten de coalitie.

        :param agent: De agent om te evalueren
        :param coalitions: List of all coalitions
        :return: None
        """
        # print(f'\t{self.coalition}\t{agent.coalition}')

        if self.coalition is None and agent.coalition is None:
            temp_coalition = Coalition(color=(0, 0, 0), members=[self, agent])
            if self.evaluate_coalition_membership(coalition=temp_coalition, coalitions=coalitions) is False:
                temp_coalition.disband_coalition()
        elif self.coalition is None and agent.coalition is not None:
            agent.coalition.add_player(member=self)
            if self.evaluate_coalition_membership(coalition=agent.coalition, coalitions=coalitions) is False:
                agent.coalition.remove_player(member=self)
        elif self.coalition is not None and agent.coalition is None:
            original_coalition = self.coalition
            original_coalition.add_player(member=agent)
            if agent.evaluate_coalition_membership(coalition=original_coalition, coalitions=coalitions) is False:
                original_coalition.remove_player(member=agent)
        elif (self.coalition is not None and agent.coalition is not None) and self.coalition == agent.coalition:
            if self.evaluate_coalition_membership(coalition=self.coalition, coalitions=coalitions) is False:
                self.coalition.remove_player(agent)

    def evaluate_coalition_membership(self, coalition: Coalition, coalitions: List[Coalition]) -> bool:
        """
        Evalueer of een agent zich moet aansluiten bij, blijven in of verlaten van een coalitie op basis van
        de waarde die de agent zou hebben binnen en buiten de coalitie.

        :param coalition: De coalitie om te evalueren
        :param coalitions: List of all coalitions
        :return: None
        """
        value_outside_coalition = self.calculate_agent_value_without_coalition()
        value_inside_coalition = self.calculate_agent_value_with_coalition(coalition=coalition)
        # print(f'\t{value_outside_coalition = }\t{value_inside_coalition = }\t{coalition.members.__str__()}')

        if value_inside_coalition >= value_outside_coalition:  # The agent should join or stay in the coalition
            if coalition.color == (0, 0, 0):
                self.coalition.disband_coalition()
                self.empty_coalition(coalitions=coalitions).add_player(self)
            return True
        else:  # The agent should leave the coalition or not join
            # TODO fight or run from other player
            return False

    def calculate_agent_value_without_coalition(self) -> float:
        """
        Bereken de waarde van de agent buiten een coalitie op basis van hun military strength, resourcefulness en
        zijn situatie.

        :return: De waarde van de agent buiten een coalitie
        """
        return self.agent_values['Strength'] * self.determine_weights_individual()["Resourcefulness"] + \
               self.agent_values['Resourcefulness'] * self.determine_weights_individual()["Military Strength"]

    def calculate_agent_value_with_coalition(self, coalition: Coalition):
        """
        Bereken de waarde van de agent binnen de gegeven coalitie op basis van hun military strength,
        resourcefulness en de situatie van de coalitie.

        :param coalition: De coalitie om te evalueren
        :return: De waarde van de agent binnen de coalitie
        """
        total_value = (coalition.total_resourcefulness() * self.determine_weights_coalition(coalition)["Resourcefulness"]) + \
                      (coalition.total_strength() * self.determine_weights_coalition(coalition)["Military Strength"])
        return total_value / len(coalition.members) if self in coalition.members \
            else total_value / (len(coalition.members) + 1)

    def determine_weights_individual(self) -> dict:
        """
        Bepaal het belang van military strength en resourcefulness voor een agent op basis van hun health en
        hongersituatie. Bepaal eerst de waarde dat de agent hecht aan military strength. Hoe lager de average health, hoe meer waardevol
        hij denkt dat hij is. Als average health hoger is dan 90%, dan hecht je weinig waarde aan strength. Als average
        health hoger is dan 50%, dan hecht je een beetje waarde aan strength. Als average health lager is dan 50%, dan
        hecht je veel waarde aan strength. Bepaal daarna de waarde dat de agent hecht aan resourcefulness. Hoe lager het
        aantal voedsel dat de coalitie heeft, hoe meer waardevol hij denkt dat hij is. Als average food hoger is dan
        90%, dan hecht je weinig waarde aan resourcefulness. Als average food hoger is dan 50%, dan hecht je wat waarde
        aan resourcefulness. Als average health lager is dan 50%, dan hecht je veel waarde aan strength.

        :return: Een dictionary met de gewichten voor military strength en resourcefulness
        """
        weight_military_strength = 1 if self.health / self.max_health > 0.5 else 1.25
        weight_resourcefulness = 1 if self.hunger / self.max_hunger > 0.5 else 1.25
        return {"Military Strength": weight_military_strength, "Resourcefulness": weight_resourcefulness}

    def determine_weights_coalition(self, coalition: Coalition) -> dict:
        """
        Bepaal het belang van military strength en resourcefulness voor een coalitie op basis van de gemiddelde health
        en voedselsituatie van de coalitie. Bepaal eerst de waarde dat de coalitie hecht aan military strength. Hoe
        lager de average health, hoe hoger de weight. Als average health hoger is dan 90%, dan hecht de coalitie weinig
        waarde aan strength. Als average health hoger is dan 50%, dan hecht de coalitie wat waarde aan strength. Als
        average health lager is dan 50%, dan hecht de coalitie veel waarde aan strength. Bepaal daarna de waarde dat de
        coalitie hecht aan resourcefulness. Hoe lager het aantal voedsel dat de coalitie heeft, hoe hoger de weight. Als
        average food hoger is dan 90%, dan hecht de coalitie weinig waarde aan resourcefulness. Als average food hoger
        is dan 50%, dan hecht de coalitie wat waarde aan resourcefulness. Als average health lager is dan 50%, dan hecht
        de coalitie veel waarde aan strength.

        :param coalition: De coalitie om te evalueren
        :return: Een dictionary met de gewichten voor military strength en resourcefulness
        """
        weight_military_strength = 1 if coalition.average_health() > 0.5 else 1.25
        weight_resourcefulness = 1 if coalition.average_food() > 0.5 else 1.25
        return {"Military Strength": weight_military_strength, "Resourcefulness": weight_resourcefulness}

    def update_behaviour(self, tiles: [[Tile]], timestep: int) -> None:
        """
        :param tiles: The entire grid
        :param timestep: Game timestep
        :return: None
        """
        action = self.choose_action(tiles=tiles)  # Kies een actie
        self.perform_action(action=action, tiles=tiles)  # Voer de gekozen actie uit

        self.update_memory(timestep=timestep, tiles=tiles)  # Update memory
        self.update_hunger(amount=-1)  # Verander honger met -1

    def choose_action(self, tiles: [[Tile]]) -> str:
        """
        :param tiles: The entire grid
        :return: One of the possible actions; "Random Move" or "Go To Highest Food Probability"
        """
        # TODO Vechten als agents geen coalitie willen vormen toevoegen.
        if self.hunger > self.max_hunger / 2:  # Beweeg random als de agent boven max_hunger / 2 is
            return "Random Move"
        elif self.hunger <= self.max_hunger / 2:  # Ga naar voedsel met hoogste kans op voedsel
            probabilities = self.calculate_food_probabilities(tiles, False)
            for tile, probability in probabilities.items():
                if tile not in self.has_visited:
                    return "Go To Highest Food Probability"
            return "Random Move"  # Als er geen tiles zijn, dan random move

    def perform_action(self, action: str, tiles: [[Tile]]) -> None:
        # TODO Docstring toevoegen.
        if action == "Random Move":
            self.random_move(tiles, tiles[0][0].size)
        elif action == "Go To Highest Food Probability":
            self.go_to_highest_food_probability(tiles)

    def go_to_highest_food_probability(self, tiles: [[Tile]]) -> None:
        # TODO Docstring toevoegen.
        probabilities = self.calculate_food_probabilities(tiles, False)

        detected_food = self.detect_food(tiles)  # Check if the player finds food, else this variable is None
        if detected_food:  # If the player found food
            goal = max(detected_food, key=lambda k: detected_food[k])  # Target tile for the agent
            self.move((goal.x + 15 - (self.x + 15)) // (self.radius * 2),
                      (goal.y + 15 - (self.y + 15)) // (self.radius * 2), tiles)  # Move the player closer to the tile
        else:
            for tile, probability in probabilities.items():  # Ga naar tile waar hij nog niet is geweest.
                if tile.index() == self.index() and tile not in self.has_visited:  # Als de player op een tile zit in de lijst, voeg hem dan aan de lijst
                    self.has_visited.append(tile)
                elif tile not in self.has_visited:
                    self.go_to_tile(tile, tiles)
                    break

    def index(self) -> (int, int):
        """
        Get the current position of the agent based on coordinates.

        :return: Tuple (int, int): x and y coordinates of agent
        """
        return self.x // self.speed, self.y // self.speed

    def add_grids(self, x: int, y: int, minimum=0, maximum=19) -> [(int, int)]:
        """
        Get the indexes of the possible grids.

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
        :param tiles: The entire Grid
        :return: A list with all adjacent tiles
        """
        x, y = self.index()  # Current position
        return [tiles[x][y] for x, y in
                self.add_grids(x=x, y=y) + [coords[::-1] for coords in self.add_grids(x=y, y=x)]]

    def move(self, dx: int, dy: int, tiles: [[Tile]]) -> bool:
        """
        Set the next x- and y-coordinates for the Agent.

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
            return True
        else:
            return False

    def go_to_tile(self, tile: Tile, tiles: [[Tile]]) -> None:
        """
        Calculates what the next x- and y-coordinates are.

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

    def move_direction(self, tiles: [[Tile]]) -> bool:
        """
        Move the agent to a direction.

        :param tiles: The entire Grid
        :return: None
        """
        self.amount_of_steps -= 1
        if self.direction == "north":
            return self.move(0, -1, tiles)
        elif self.direction == "east":
            return self.move(1, 0, tiles)
        elif self.direction == "south":
            return self.move(0, 1, tiles)
        elif self.direction == "west":
            return self.move(-1, 0, tiles)

    def detect_food(self, tiles: [[Tile]]) -> dict:
        """
        See if there is food in adjacent tiles.

        :param tiles: The entire Grid
        :return: Dictionary of all foods in the adjacent tiles
        """
        food_dict = {}
        for tile in self.get_adjacent_tiles(tiles):
            for object in tile.objects:
                if isinstance(object, Food):
                    food_dict[tile] = food_dict.get(tile, 0) + 1
        return food_dict

    def calculate_food_probabilities(self, tiles: [[Tile]], update_probability: bool) -> dict:
        """
        Calculate the probability of finding food.

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
        :param tiles: The entire Grid
        :return: None
        """
        self.map_has_visited = [[0 for num_tile in range(len(tiles))] for tile in tiles]

    def update_memory(self, timestep: int, tiles: [[Tile]]) -> None:
        """
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

        max_value = max(directions.values())
        max_keys = [key for key, value in directions.items() if value == max_value]
        random_key = random.choice(max_keys)
        return random_key

    def draw(self, screen: pygame.surface.Surface, index: int) -> None:
        """
        Draw the agent, its label, hunger and health bar.

        :param screen: Pygame surface
        :param index: Index of the agent
        :return: None
        """
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        # Create a label
        label_text = pygame.font.SysFont('Arial', 18).render(str(index), True, (255, 255, 255))
        screen.blit(label_text, label_text.get_rect(center=(self.x, self.y)))

        # Calculate the percentage of hunger remaining
        percent_remaining = self.hunger / self.max_hunger
        # Calculate the color of the hunger bar
        bar_color = (0, 255, 0) if percent_remaining > 0.5 \
            else (255, 255, 0) if percent_remaining > 0.25 else (255, 0, 0)
        # Draw the hunger bar
        pygame.draw.rect(screen, (128, 128, 128), (self.x - self.radius, self.y + self.radius + 5, self.radius * 2, 10))
        pygame.draw.rect(screen, bar_color, (self.x - self.radius, self.y + self.radius + 5,
                                             self.radius * 2 * percent_remaining, 10))

        # Calculate the percentage of health remaining
        percent_remaining = self.health / self.max_health
        # Calculate the color of the health bar
        bar_color = (0, 255, 0) if percent_remaining > 0.5 \
            else (255, 255, 0) if percent_remaining > 0.25 else (255, 0, 0)
        # Draw the health bar
        pygame.draw.rect(screen, (128, 128, 128), (self.x - self.radius, self.y - self.radius - 10, self.radius * 2, 5))
        pygame.draw.rect(screen, bar_color, (self.x - self.radius, self.y - self.radius - 10,
                                             self.radius * 2 * percent_remaining, 5))

    def update_hunger(self, amount: int) -> None:
        """
        :param amount: The change in hunger
        :return: None
        """
        self.hunger += amount
        if self.hunger > self.max_hunger:
            self.hunger = self.max_hunger
        elif self.hunger < 0:
            self.hunger = 0

    def update_health(self, amount: int) -> None:
        """
        :param amount: The change in health
        :return: None
        """
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health
        elif self.health < 0:
            self.health = 0

    def use_weapon(self) -> int:
        if self.weapon is not None:  # If the agent has a weapon
            base_damage = self.damage + self.weapon.damage
        else:
            base_damage = self.damage
        return random.randint(base_damage - 2, base_damage + 2)

    def random_move(self, tiles: [[Tile]], TILE_SIZE: int) -> None:
        """
        Move the player to a random tile.

        :param tiles: The entire Grid
        :param TILE_SIZE: The tile size from config
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
            success = self.move_direction(tiles)  # Move the player with different logic
            if not success:
                self.direction = self.choose_direction(tiles, 3)  # Choose a new direction if the move was out of bounds
                self.amount_of_steps = 3

    def collision_player(self, enemy) -> bool:
        """
        :param enemy: Other player
        :return: boolean
        """
        distance = ((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2) ** 0.5
        if distance < self.radius + enemy.radius:
            enemy.health -= self.use_weapon()
            self.health -= enemy.use_weapon()
            return True
        return False

    def collision_food(self, food: Food, tiles: [[Tile]]) -> bool:
        """
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

    def collision_weapon(self, weapon, tiles: [[Tile]]) -> bool:
        """
        :param weapon: Weapon object
        :param tiles: The entire grid
        :return: boolean
        """
        distance = ((self.x - weapon.x) ** 2 + (self.y - weapon.y) ** 2) ** 0.5
        if distance < self.radius + weapon.size:
            weapon.collision_detected(self)
            x, y = self.index()
            tiles[x][y].objects.remove(weapon)
            return True
        return False

    def can_communicate(self, tiles: [[Tile]]) -> Tuple[bool, Any]:
        """
        Check if agent is next to another agent.

        :param tiles: The entire grid
        :return: Tuple of boolean (able to communicate) and nearby agent
        """
        x, y = self.index()
        for object in tiles[x][y].objects:
            if object != self and Player == type(object):
                return True, object
        for adjacent_tile in self.get_adjacent_tiles(tiles=tiles):
            for object in adjacent_tile.objects:
                if object != self and Player == type(object):
                    return True, object
        return False, None
