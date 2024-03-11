import pygame
import random
import sys
from agents.enemy import Enemy
from agents.player import Player
from food import Food 
from tile import Tile
from weapon import Weapon
from object_spawner import ObjectSpawner


def move_enemies(enemies: [Enemy], tiles: [[Tile]]) -> None:
    """
    Move an Enemy Agent to a tile.
    :param enemies: Enemy Agent
    :param tiles: The next tile that the Enemy Agent is supposed to move ot
    :return: None
    """
    for enemy in enemies:
        enemy.move(WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE, tiles)


def get_random_tile(tiles: [[Tile]]) -> Tile:
    """
    Get a random tile fromt he grid
    :param tiles: The entire Grid
    :return: A random tile from the Grid
    """
    return random.choice(random.choice(tiles))


def random_move(tiles: [[Tile]]) -> None:
    """
    Move the player to a random tile.
    :param tiles: The entire Grid
    :return: None
    """
    if player.amount_of_steps == 0:  # If the player is in its starting position
        player.direction = player.choose_direction(tiles, 3)
        player.amount_of_steps = 3  # Add amount of taken steps to agent
    detected_food = player.detect_food(tiles)  # Check if the player finds food, else this variable is None
    if detected_food:  # If the player found food
        goal = max(detected_food, key=lambda k: detected_food[k])  # Target tile for the agent
        player.move((goal.x + 15 - (player.x + 15)) // TILE_SIZE, (goal.y + 15 - (player.y + 15)) // TILE_SIZE, tiles)  # Move the player closer to the tile
    else:
        player.move_direction(tiles)  # Move the player with different logic


pygame.init()

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
TILE_SIZE = 30
TILES_WIDE = WINDOW_WIDTH // TILE_SIZE
TILES_HIGH = WINDOW_HEIGHT // TILE_SIZE

screen = pygame.display.set_mode(size=(WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Hunger Games')

clock = pygame.time.Clock()

tiles = [[Tile(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2, TILE_SIZE, (255, 255, 255)) for y in range(TILES_HIGH)] for x in range(TILES_WIDE)]

enemies = []
random_tile = get_random_tile(tiles)
weapons = [Weapon(random_tile.x, random_tile.y, TILE_SIZE // 2, (255, 215, 100), True, 6)]
random_tile.objects.append(weapons[0])
random_tile = get_random_tile(tiles)
foods = [Food(random_tile.x, random_tile.y, TILE_SIZE // 2, (0, 255, 0), True)]
random_tile.objects.append(foods[0])

spawner = ObjectSpawner(TILES_WIDE, TILES_HIGH)
spawner.set_specific_chance_in_grid(10, 10, 200)

# Initialize enemies randomly
for i in range(5):
    random_tile = get_random_tile(tiles)
    enemy_radius = TILE_SIZE // 2
    enemy_color = (255, 0, 0)
    enemies.append(Enemy(random_tile.x, random_tile.y, enemy_radius, enemy_color, TILE_SIZE, 20, random_tile))

random_tile = get_random_tile(tiles)
player = Player(random_tile.x, random_tile.y, TILE_SIZE // 2, (0, 0, 255), TILE_SIZE, 40, 20)
player.reset_map(tiles)
collision_occured = False

found_food_when_hungry = False
timestep = 0
while True:
    for event in pygame.event. get():
        if event.type == pygame.QUIT:
            pygame.quit() 
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                timestep += 1

                if player.hunger > player.max_hunger / 2:
                    random_move(tiles=tiles)

                elif player.hunger <= player.max_hunger / 2 and found_food_when_hungry is False:  # Heeft honger
                    tile = player.max_food_probability(tiles, False)
                    if tile is None:  # Geen food op tile waar hij is gegaan
                        found_food_when_hungry = True
                    else:
                        player.max_food_probability(tiles, True)
                        player.go_to_tile(tile, tiles)  # Loop naar tile

                else:   # Doe random
                    if player.hunger == 0:
                        print('Game over')
                    else:
                        random_move(tiles=tiles)

                move_enemies(enemies, tiles)
                player.update_memory(timestep, tiles)
                player.update_hunger(-1)
                collision_occured = False
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
    player.draw(screen)

    # Draw enemies
    for enemy in enemies:
        enemy.draw(screen)

    # Draw weapons
    for weapon in weapons:
        weapon.draw(screen)

    # Draw foods
    for food in foods:
        food.draw(screen)

    # Check collision between player and enemies
    if not collision_occured:
        for enemy in enemies:
            distance = ((player.x - enemy.x) ** 2 + (player.y - enemy.y) ** 2) ** 0.5
            if distance < player.radius + enemy.radius:
                enemy.health -= player.use_weapon()
                player.health -= enemy.use_weapon()
                collision_occured = True
                #player.remember_attack(timestep, enemy)
                print("Player collided with enemy")

    # Check collision between player and weapons
    for weapon in weapons:
        distance = ((player.x - weapon.x) ** 2 + (player.y - weapon.y) ** 2) ** 0.5
        if distance < player.radius + weapon.size:
            weapon.collision_detected(player)
            weapons.remove(weapon)
            x, y = player.index()
            tiles[x][y].objects.remove(weapon)
            print(f"Player collided with weapon")

    # Check collisions between player and foods
    for food in foods:
        distance = ((player.x - food.x) ** 2 + (player.y - food.y) ** 2) ** 0.5
        if distance < player.radius + food.size:
            food.collision_detected(player)
            foods.remove(food)
            x, y = player.index()
            tiles[x][y].objects.remove(food)
            print("Player collided with food")

    pygame.display.flip()
    clock.tick(60)


