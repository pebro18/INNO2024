from agents.player import Player
import itertools
import random

from collections import defaultdict, Counter

from tile import Tile
from typing import List, Dict
from math import sqrt


class AuctionManager:
    def __init__(self):
        # 0: [], 1 : []
        self.teams_dict = {}

    def add_teams_with_players(self, players: List[Player]):
        """
        Add team to self.teams_dict
        :param players: A list of all players belonging to the team
        """
        self.teams_dict[len(self.teams_dict)] = players

    def get_team(self, team_number: int):
        """
        Return a list of players given a team ID
        :param team_number: Team number to identify the teams
        :return: List of Players in given team
        """
        return self.teams_dict[team_number]

    def delete_team(self, team_number: int):
        """
        Delete a team given a team number
        :param team_number: Team number to identify the teams
        """
        self.teams_dict.pop(team_number)

    def add_player(self, player: Player, team_number: int):
        """
        Add player to a team
        :param player: Player
        :param team_number: Team number to identify the teams
        """
        self.teams_dict[team_number].append(player)
    
    def get_team_number_from_player(self, player: Player) -> int:
        """
        Find in which team a Player is in
        :param player: Player
        :return: Team number
        """
        for team_number, team in self.teams_dict.items():
            if player in team:
                return team_number

    def start_auction(self, tiles, team_number: int):
        """
        Auction algorithm; divide tasks between agents in a team
        :param tiles: The grid
        :param team_number: Team number to identify the teams
        :return:
        """
        selected_team = self.get_team(team_number)
        N = len(selected_team)  # Amount of team members
        M = self.get_postions_of_food_from_teams(team_number, tiles)  # Tasks
        if M is None:  # If there are no tasks
            return "Random Move"
        
        sequence = []

        agents = {}
        prices = {}
        unassigned = []
        values_matrix = []

        for i in range(len(M)):
            sequence.append(i)

        for i in range(0, int(N)):
            sublist = []
            # TODO: Change this to the closest food position
            team_info = self.get_team(team_number)
            player_info = team_info[i]    
            top_list = self.top_closest_location_list(player_info, M)
            for k in range(0, int(N)):
                val = top_list[k]
                sublist.append(val)
            values_matrix.append(sublist)

        for p, player in enumerate(selected_team):
            agents[p] = None
            prices[p] = 0

        while (None in agents.values()):

            unassigned_agent = self.findUnmatchedAgent(agents)
            agents_row = values_matrix[unassigned_agent]

            max_diff = 0
            max_obj = 0
            for j in range(0, int(N)):
                value = agents_row[j] - prices[j]
                if value > max_diff:
                    max_diff = value
                    max_obj = j

            next_max_diff = 0
            for l in range(0, int(N)):
                value = agents_row[l] - prices[l]
                if value > next_max_diff and value < max_diff:
                    next_max_diff = value

            bid_increment = max_diff - next_max_diff
            agents[unassigned_agent] = max_obj

            for key, value in agents.items():
                if value is max_obj and key is not unassigned_agent:
                    agents[key] = None
                    unassigned.append(key)

            prices[max_obj] += bid_increment

        for key, value in agents.items():
            print("Agent " + str(key) + " is assigned to object " + str(value))
            self.give_player_assignment(selected_team[key], M[value])

    
    def top_closest_location_list(self, agent, locations): 

        sort_list = []
        for i in range(len(locations)):
            temp_location = self.get_distance(agent, locations[i])
            sort_list.append(temp_location)

        top_list = []
        for i in range(len(sort_list)):
            top_list.append(sort_list.index(min(sort_list)))
            sort_list[sort_list.index(min(sort_list))] = 999      
        return top_list
    
    def get_distance(self, agent, location):
        return sqrt((agent.x - location.x)**2 + (agent.y - location.y)**2)

    def findUnmatchedAgent(self, agents):
        for key, value in agents.items():
            if value is None:
                return key

    def give_player_assignment(self, agent: Player, task):
        agent.recieve_assignment(task)

    def get_player_food_probabilty(self, player: Player, tiles):
        return player.go_to_highest_food_probability(tiles)

    def combine_memories(self, memories: List[Dict[Tile, float]]):
        """
        Combine the seperate memories into one memory where all probabilities are averaged out
        :param memories: Memory of every agent of the tiles where they found food
        :return: Every tile that the agents have previously found food on and their probabilities.
        """
        combined_mem = defaultdict(list)  # Will look like this: {Tile: [0.4], Tile2:[0.5, 0.3, 0.4], ... Tile999:[0.25]
        # Combine memories
        for memory in memories:
            for key, value in memory.items():
                combined_mem[key].append(value)

        averaged_memory = {}
        # Average out probabilities for every tile
        for tile, probability in combined_mem.items():
            averaged_memory[tile] = sum(probability)/len(probability)

        return averaged_memory

    def create_tasks(self, team_memory, team_number):
        """
        Create the correct amount of tasks, one for each agent.
        :param team_memory: Tiles with averaged probability
        :param team_number: Team number to refer to the correrct team
        :return: List of N (=amount of Agents) tiles to go to (tasks)
        """
        tasks = list(team_memory.keys())
        count = 0
        while len(tasks) < len(self.teams_dict[team_number]):  # While there are less tiles than amount of agents
            tasks.append(tasks[count])
            count += 1

        while len(tasks) > len(self.teams_dict[team_number]):  # While there are more  tiles than amount of agents
            counter_dict = Counter(team_memory)
            team_memory = counter_dict.most_common(len(self.teams_dict[team_number]))
            tasks = [task[0] for task in team_memory]
        
        return tasks

    def get_postions_of_food_from_teams(self, team_number: int, tiles):
        """
        Collect all agent memories, combine them, and return N (= amount of Agents) tasks.
        :param team_number: Number to identify team/coalition
        :param tiles: The entire grid
        :return: N (=amount of Agents) amount of tasks
        """
        team = self.get_team(team_number)
        collectieve_memory = [team[0].calculate_food_probabilities(tiles, False)]  # TODO: Placeholder, delete this
        # collectieve_memory = [player.memory for player in team]

        # Combine the memories into one big 'team-brain'
        team_memory = self.combine_memories(collectieve_memory)
        
        if team_memory == {}:
            return None

        # Create and return tasks
        return self.create_tasks(team_memory, team_number)