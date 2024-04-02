import pygame
import random
import sys
from player import Player
from food import Food
from tile import Tile
from weapon import Weapon
from object_spawner import ObjectSpawner
from config import *


def get_random_tile(tiles: [[Tile]]) -> Tile:
    """
    Get a random tile from the grid
    :param tiles: The entire Grid
    :return: A random tile from the Grid
    """
    return random.choice(random.choice(tiles))


def check_collision(players: [Player], object: Weapon or Food, tiles: [[Tile]]) -> bool:
    if type(object) == Weapon:
        for player in players:
            if player.collision_weapon(weapon=object, tiles=tiles):
                return True
    elif type(object) == Food:
        for player in players:
            if player.collision_food(food=object, tiles=tiles):
                return True
    return False


def initialize() -> ([[Tile]], [Player], [Weapon], [Food], ObjectSpawner, pygame.surface.Surface, pygame.time.Clock):
    """
    Initialize game and set variables
    :return: Tuple that includes all initialized variables
    """
    # PyGame initialization
    pygame.init()

    # Initialize Pygame window
    screen = pygame.display.set_mode(size=(WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Hunger Games')

    # Start clock
    clock = pygame.time.Clock()

    # Create grid
    tiles = [[Tile(x=x * TILE_SIZE + TILE_SIZE // 2, y=y * TILE_SIZE + TILE_SIZE // 2, size=TILE_SIZE,
                   color=(255, 255, 255)) for y in range(TILES_HIGH)] for x in range(TILES_WIDE)]

    # Initialize weapon on random tile
    random_tile = get_random_tile(tiles)
    weapon = Weapon(x=random_tile.x, y=random_tile.y, size=TILE_SIZE // 2, color=(255, 215, 100), visible=True, damage=6)
    random_tile.objects.append(weapon)

    # Initialize food on random tile
    random_tile = get_random_tile(tiles)
    food = Food(x=random_tile.x, y=random_tile.y, size=TILE_SIZE // 2, color=(0, 255, 0), visible=True)
    random_tile.objects.append(food)

    # Initialize spawner
    spawner = ObjectSpawner(x=TILES_WIDE, y=TILES_HIGH)
    spawner.set_specific_chance_in_grid(x=10, y=10, chance=200)

    # Initialize 10 players on random tiles
    players = []
    for i in range(10):
        random_tile = get_random_tile(tiles)
        players.append(Player(x=random_tile.x, y=random_tile.y, radius=TILE_SIZE // 2, color=(0, 0, 255), speed=TILE_SIZE,
                              max_hunger=40, max_health=20))
        players[i].reset_map(tiles)
        x, y = random_tile.index()
        tiles[x][y].append(player=players[i])

    return tiles, players, weapon, food, spawner, screen, clock


def main(tiles: [[Tile]], players: [Player], weapons: [Weapon], foods: [Food], spawner: ObjectSpawner,
         screen: pygame.surface.Surface, clock: pygame.time.Clock, timestep=0) -> None:
    """
    Run the game
    :param tiles: The entire Grid
    :param players: The agents
    :param weapons: List of all weapons
    :param foods: List of all foods
    :param spawner: The object spawner
    :param screen: Pygame surface
    :param clock: Pygame clock
    :return: None
    """
    digits = list(range(49, 58)) + [pygame.K_0]
    keys = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
    differences = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    selected_player = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    timestep += 1

                    for player in players:
                        player.update_behaviour(tiles=tiles, timestep=timestep)

                    food = spawner.spawn_food(tiles)
                    if food is not None:
                        foods.append(food)

                # TODO: Dit is code om een player te besturen met pijltjes, na het testen weghalen
                if event.key in digits:
                    index = digits.index(event.key)
                    try:
                        selected_player = players[index]
                    except IndexError:
                        print(f'Player {index + 1} not initiated')
                elif event.key in keys and selected_player is None:
                    print(f'No player selected')

                if event.key in keys and selected_player is not None:
                    timestep += 1

                    dx, dy = differences[keys.index(event.key)]
                    selected_player.move(dx=dx, dy=dy, tiles=tiles)
                    selected_player.update_memory(timestep=timestep, tiles=tiles)  # Update memory
                    selected_player.update_hunger(amount=-1)  # Change hunger with -1

                    food = spawner.spawn_food(tiles)
                    if food is not None:
                        foods.append(food)

                for player in players:
                    if player.can_communicate(tiles=tiles):
                        print(f'{player} can communicate')

        # Fill background
        screen.fill((255, 255, 255))

        # Draw tiles
        for x in range(TILES_WIDE):
            for y in range(TILES_HIGH):
                tiles[x][y].draw(screen)

        # Draw player
        for player in players:
            player.draw(screen)

        # Draw weapon
        for weapon in weapons:
            weapon.draw(screen)

        # Draw foods
        for food in foods:
            food.draw(screen)

        # Check collision between player and weapons
        for weapon in weapons:
            if check_collision(players=players, object=weapon, tiles=tiles):
                weapons.remove(weapon)

        # Check collisions between player and foods
        for food in foods:
            if check_collision(players=players, object=food, tiles=tiles):
                foods.remove(food)

        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    tiles, players, weapon, food, spawner, screen, clock, = initialize()

    main(tiles=tiles, players=players, weapons=[weapon], foods=[food], spawner=spawner, screen=screen, clock=clock)
