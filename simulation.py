from player import Player
from food import Food
from tile import Tile
from weapon import Weapon
from object_spawner import ObjectSpawner
from coalition import Coalition
from config import *
from typing import List, Tuple


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
            players.remove(player)
            x, y = player.index()
            tiles[x][y].objects.remove(player)
            if player.coalition is not None:
                player.coalition.remove_player(member=player)

        boolean, object = player.can_communicate(tiles=tiles)
        if boolean:
            player.evaluate_coalition_with_individual(agent=object, coalitions=coalitions)


def simulation(tiles: [[Tile]], players: [Player], weapons: [Weapon], foods: [Food], spawner: ObjectSpawner,
               coalitions: [Coalition], screen: pygame.surface.Surface, clock: pygame.time.Clock, timestep=0,
               max_timestep=None) -> Tuple[int, List[int]]:
    """
    Simulate the game.

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
    while timestep < max_timestep:
        timestep += 1

        for player in players:
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

        if not timestep < max_timestep:
            total_diversity = 0

            coalition_count = 0
            player_count = 0
            average_resourcefulness = 0
            average_strength = 0
            for coalition in coalitions:
                if coalition.members:
                    coalition_count += 1
                    total_diversity += coalition.determine_diversity()
            for player in players:
                player_count += 1
                average_strength += player.agent_values['Strength']
                average_resourcefulness += player.agent_values['Resourcefulness']

            total_stats = [coalition_count, player_count, average_strength / player_count, average_resourcefulness / player_count]
            return total_diversity, total_stats