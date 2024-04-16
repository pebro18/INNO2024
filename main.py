import pygame
import random
import sys
from agents.enemy import Enemy
from agents.player import Player
from food import Food
from tile import Tile
from object_spawner import ObjectSpawner
from config import *
from auction.auction_manager import AuctionManager


def get_random_tile(tiles: [[Tile]]) -> Tile:
    """
    Get a random tile from the grid
    :param tiles: The entire Grid
    :return: A random tile from the Grid
    """
    return random.choice(random.choice(tiles))


def initialize() -> ([[Tile]], Player, [Enemy], [Food], ObjectSpawner, pygame.surface.Surface, pygame.time.Clock):
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


    spawner = ObjectSpawner(TILES_WIDE, TILES_HIGH)
    spawner.set_specific_chance_in_grid(10, 10, 5)
    spawner.set_specific_chance_in_grid(5, 4, 5)

    # Initialize 5 enemies on random tiles
    enemies = [Enemy(x=random_tile.x, y=random_tile.y, radius=TILE_SIZE // 2, color=(255, 0, 0), speed=TILE_SIZE,
                     max_health=20, current_tile=random_tile) for random_tile in
               [get_random_tile(tiles=tiles) for count in range(5)]]

    random_tile = get_random_tile(tiles)
    player = Player(x=random_tile.x, y=random_tile.y, radius=TILE_SIZE // 2, color=(0, 0, 255), speed=TILE_SIZE,
                    max_hunger=40, max_health=20)
    player.reset_map(tiles)

    auction_manager = AuctionManager()

    return tiles, player, enemies, weapon, food, spawner, auction_manager, screen, clock


def initialize_auction_experiment() -> ([[Tile]], Player, [Enemy], [Food], ObjectSpawner, pygame.surface.Surface, pygame.time.Clock):
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

    spawner = ObjectSpawner(TILES_WIDE, TILES_HIGH)
    spawner.set_specific_chance_in_grid(10, 10, 5)
    spawner.set_specific_chance_in_grid(5, 4, 5)

    random_tile = get_random_tile(tiles)
    food = Food(x=random_tile.x, y=random_tile.y, size=TILE_SIZE // 2, color=(0, 255, 0), visible=True)
    random_tile.objects.append(food)

    enemies = []

    auction_manager = AuctionManager()

    player_team_1 = []
    for i in range(5):
        player = Player(x= TILE_SIZE // 2, y= TILE_SIZE // 2 + ((TILE_SIZE * 4) * i), radius=TILE_SIZE // 2, color=(0, 0, 255), speed=TILE_SIZE,
                        max_hunger=40, max_health=20, auction_manager=auction_manager) 
        player.reset_map(tiles)
        player_team_1.append(player)

    player_team_2 = []
    for i in range(5):  
        player = Player(x= TILE_SIZE * TILES_WIDE - TILE_SIZE // 2, y= TILE_SIZE // 2 + ((TILE_SIZE * 4) * i), radius=TILE_SIZE // 2, color=(255, 0, 0), speed=TILE_SIZE,
                        max_hunger=40, max_health=20)
        player.reset_map(tiles)
        player_team_2.append(player)

    auction_manager.add_teams_with_players(player_team_1)
    auction_manager.add_teams_with_players(player_team_2)

    players = player_team_1 + player_team_2
    return tiles, players, enemies, food, spawner, auction_manager, screen, clock


def main(tiles: [[Tile]], player: Player, enemies: [Enemy], foods: [Food], spawner: ObjectSpawner,
         auction_manager: AuctionManager, screen: pygame.surface.Surface, clock: pygame.time.Clock,
         found_food_when_hungry=False, collision_occured=False, timestep=0) -> None:
    """
    Run the game
    :param tiles: The entire Grid
    :param player: The agent
    :param enemies: List of all enemies
    :param weapons: List of all weapons
    :param foods: List of all foods
    :param spawner: The object spawner
    :param screen: Pygame surface
    :param clock: Pygame clock
    :return: None
    """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit() 
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    timestep += 1
                    for p in player:
                         p.update_behaviour(tiles, timestep)  
                    # for enemy in enemies:
                    #     enemy.move(tiles=tiles,
                    #                WINDOW_WIDTH=WINDOW_WIDTH,
                    #                WINDOW_HEIGHT=WINDOW_HEIGHT,
                    #                TILE_SIZE=TILE_SIZE
                    #                )
                    collision_occured = False
                    for _ in range(4):  # TODO: Remove or edit
                        food = spawner.spawn_food(tiles)
                        if food is not None:
                            foods.append(food)

        # Fill background
        screen.fill((255, 255, 255))

        # Draw tiles
        for x in range(TILES_WIDE):
            for y in range(TILES_HIGH):
                tiles[x][y].draw(screen)

        # Draw player
        for p in player:
            p.draw(screen)

        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen)

        # Draw foods
        for food in foods:
            food.draw(screen, FOOD_IMAGE)

        # Check collision between player and enemies
        if not collision_occured:
            for enemy in enemies:
                for p in player:
                    if p.collision_enemy(enemy=enemy):
                        collision_occured = True

        # Check collision between player and weapons
        # for weapon in weapons:
        #     if player.collision_weapon(weapon=weapon, tiles=tiles):
        #         weapons.remove(weapon)

        # Check collisions between player and foods
        for food in foods:
            for p in player:
                if p.collision_food(food=food, tiles=tiles):
                    if food in foods:
                        foods.remove(food)

        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    tiles, agent, enemies, food, spawner, auction_manager, screen, clock, = initialize_auction_experiment()

    main(tiles, agent, enemies, [food], spawner, auction_manager, screen, clock)