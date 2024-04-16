import random
import sys
from player import Player
from food import Food
from tile import Tile
from weapon import Weapon
from object_spawner import ObjectSpawner
from coalition import Coalition
from config import *
from typing import List, Tuple
from simulation import simulation
import pandas as pd


def get_random_tile(tiles: List[List[Tile]]) -> Tile:
    """
    Get a random tile from the grid

    :param tiles: The entire Grid
    :return: A random tile from the Grid
    """
    return random.choice(random.choice(tiles))


def check_collision(players: List[Player], object: Player or Weapon or Food, tiles: List[List[Tile]]) -> bool:
    """
    Check collision with other player, weapon or food.

    :param players: List of all players
    :param object: Player, Weapon or Food
    :param tiles: The entire grid
    :return: Boolean
    """
    if type(object) == Player:
        for player in players:
            if player != object and (player.coalition != object.coalition):
                if player.collision_player(enemy=object):
                    return True
    elif type(object) == Weapon:
        for player in players:
            if player.collision_weapon(weapon=object, tiles=tiles):
                return True
    elif type(object) == Food:
        for player in players:
            if player.collision_food(food=object, tiles=tiles):
                return True
    return False


def create_teams(players: List[Player], per_team: int, colors: List[Tuple[int, int, int]]) -> List[Coalition]:
    """
    Create pre-determined-size teams.

    :param players: List of all players
    :param per_team: Team size
    :param colors: List of 10 random colors
    :return: List of coalitions
    """
    team_count = len(players) / per_team
    if team_count == 1:
        return [Coalition(color=colors[0], members=players)]
    elif team_count > 1:
        teams = [players[team:team + per_team] for team in range(0, len(players), per_team)]
        return [Coalition(color=colors[teams.index(team)], members=team) for team in teams]


def create_player(tiles: List[List[Tile]], strength: int, resourcefulness: int) -> Player:
    """
    Initialize player on random tile.

    :param tiles: The entire grid
    :param strength: Strength of the player
    :param resourcefulness: Resourcefulness of the player
    :return: Initialized player
    """
    random_tile = get_random_tile(tiles)
    player = Player(x=random_tile.x, y=random_tile.y, radius=TILE_SIZE // 2, color=(0, 0, 255), speed=TILE_SIZE,
                    max_hunger=40, max_health=20, agent_values={'Strength': strength,
                                                                'Resourcefulness': resourcefulness})
    player.reset_map(tiles)
    x, y = random_tile.index()
    tiles[x][y].append(player=player)
    return player


def check_players(players: List[Player], tiles: List[List[Tile]], coalitions: List[Coalition]) -> None:
    """
    Check if player joined coalition, has died or if they are next to another (can communicate).

    :param players: List of all players
    :param tiles: The entire grid
    :param coalitions: List of all coalitions
    :return: None
    """
    for coalition in coalitions:
        if len(coalition.members) >= 2:
            average = sum([member.hunger for member in coalition.members]) // len(coalition.members)
            for member in coalition.members:
                member.hunger = average
    for player in players:
        if player.hunger == 0 or player.health <= 0:
            print(f'{player} (index={players.index(player) + 1}) died\n')
            players.remove(player)
            x, y = player.index()
            tiles[x][y].objects.remove(player)
            if player.coalition is not None:
                player.coalition.remove_player(member=player)

        boolean, object = player.can_communicate(tiles=tiles)
        if boolean:
            # print(f'{player} (index={players.index(player) + 1}) can communicate\n\t{player.agent_values = }')
            player.evaluate_coalition_with_individual(agent=object, coalitions=coalitions)
            # print()


def initialize() -> ([[Tile]], [Player], [Weapon], [Food], ObjectSpawner, [Coalition], pygame.surface.Surface,
                     pygame.time.Clock):
    """
    Initialize game and set variables.

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
    weapon = Weapon(x=random_tile.x, y=random_tile.y, size=TILE_SIZE // 2, visible=True, damage=5)
    random_tile.objects.append(weapon)

    # Initialize food on random tile
    random_tile = get_random_tile(tiles)
    food = Food(x=random_tile.x, y=random_tile.y, size=TILE_SIZE // 2, visible=True)
    random_tile.objects.append(food)

    # Initialize spawner
    spawner = ObjectSpawner(x=TILES_WIDE, y=TILES_HIGH)
    for i in range(10):
        spawner.set_specific_chance_in_grid(x=random.randint(0, 19), y=random.randint(0, 19), chance=10)
    spawner.set_specific_chance_in_grid(x=random.randint(10, 10), y=random.randint(10, 10), chance=300)

    # Initialize 10 players on random tiles
    players = []
    for i in range(4):
        players.append(create_player(tiles=tiles, strength=2, resourcefulness=2))
    for i in range(3):
        players.append(create_player(tiles=tiles, strength=1, resourcefulness=3))
    for i in range(3):
        players.append(create_player(tiles=tiles, strength=3, resourcefulness=1))

    # Initialize 10 random colors
    colors = [(250, 94, 77), (83, 166, 150), (201, 191, 49), (147, 24, 60), (229, 69, 117), (51, 153, 255),
              (181, 84, 122), (3, 216, 195), (11, 209, 155), (155, 39, 175)]
    # Create 10 empty coalitions
    coalitions = [Coalition(color=color, members=[]) for color in colors]
    # coalitions = create_teams(players=players, per_team=2, colors=colors)

    return tiles, players, weapon, food, spawner, coalitions, screen, clock


def main(tiles: [[Tile]], players: [Player], weapons: [Weapon], foods: [Food], spawner: ObjectSpawner,
         coalitions: [Coalition], screen: pygame.surface.Surface, clock: pygame.time.Clock, timestep=0) -> None:
    """
    Run the game.

    :param tiles: The entire Grid
    :param players: The agents
    :param weapons: List of all weapons
    :param foods: List of all foods
    :param spawner: The object spawner
    :param coalitions: List of all coalitions
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

                    if selected_player.hunger == 0:
                        print(f'{selected_player} (index={players.index(selected_player) + 1}) died\n')
                        players.remove(selected_player)
                        x, y = selected_player.index()
                        tiles[x][y].objects.remove(selected_player)
                        if selected_player.coalition is not None:
                            selected_player.coalition.remove_player(member=selected_player)
                        selected_player = None

                    for player in players:
                        if player != selected_player:
                            player.update_behaviour(tiles=tiles, timestep=timestep)

                    food = spawner.spawn_food(tiles)
                    if food is not None:
                        foods.append(food)

                check_players(players=players, tiles=tiles, coalitions=coalitions)
                # Check collisions between players
                for enemy in players:
                    check_collision(players=players, object=enemy, tiles=tiles)

        # Fill background
        screen.fill((255, 255, 255))

        # Draw tiles
        for x in range(TILES_WIDE):
            for y in range(TILES_HIGH):
                tiles[x][y].draw(screen=screen)

        # Draw player
        for player in players:
            player.draw(screen=screen, index=players.index(player) + 1)

        # Draw weapon
        for weapon in weapons:
            weapon.draw(screen=screen, image=WEAPON_IMAGE)

        # Draw foods
        for food in foods:
            food.draw(screen=screen, image=FOOD_IMAGE)

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
    # tiles, players, weapon, food, spawner, coalitions, screen, clock, = initialize()
    # main(tiles=tiles, players=players, weapons=[weapon], foods=[food], spawner=spawner, coalitions=coalitions,
    #      screen=screen, clock=clock)

    num_iterations = 20

    simulation_results = []

    for i in range(1, num_iterations + 1):
        tiles, players, weapon, food, spawner, coalitions, screen, clock, = initialize()
        diversity, stats = simulation(tiles=tiles, players=players, weapons=[weapon], foods=[food], spawner=spawner,
                                      coalitions=coalitions, screen=screen, clock=clock, max_timestep=500)

        print(f'Iteration {i} = Diversity: {round(diversity, 2)} Strength: {round(stats[2], 2)}, Resourcefulness: {round(stats[3], 2)}')

        simulation_results.append({
            'Iteration': i,
            'Diversity': diversity,
            'Strength': stats[2],
            'Resourcefulness': stats[3]
        })

    simulation_df = pd.DataFrame(simulation_results)

    print(simulation_df.head(10))
    simulation_df.to_csv("coalitie_data.csv", index=False)
