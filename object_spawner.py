import random
from food import Food

class ObjectSpawner:
    """This class is responsible for spawning food and weapons in the game"""

    def __init__(self,x,y):

        self.grid = [[0.1 for x in range(x)] for y in range(y)]
        self.food_list = []
        self.weapons_list = []

    def set_specific_chance_in_grid(self, x, y, chance):
        self.grid[x][y] = chance

    def choose_spawn_cell(self):
        cum_sums = []
        for row in self.grid:
            total_prob = 0
            row_probs = []
            for prob in row:
                total_prob += prob
                row_probs.append(total_prob)
            cum_sums.append(row_probs)

        cum_probs = []
        for row in cum_sums:
            max_val = row[-1]
            prob_row = [val / max_val for val in row]
            cum_probs.append(prob_row)


        cum_row_probs = []
        for i in range(len(cum_sums)):
            row_total = 0
            for j in range(len(cum_sums[i])):
                row_total += cum_sums[i][j]
            cum_row_probs.append(row_total)

        rand_row = random.choices(range(len(cum_row_probs)), weights=cum_row_probs)
        rand_col = 0
        rand_num = random.uniform(0, 1)

        for i, cum_prob in enumerate(cum_probs[rand_row[0]]):
            if rand_num < cum_prob:
                rand_col = i
                break

        return rand_row[0], rand_col
    
    def spawn_food(self, grid):
        x, y = self.choose_spawn_cell()
        if not grid[x][y].objects:
            food = Food(grid[x][y].x, grid[x][y].y, 30 // 2, True)
            grid[x][y].objects.append(food)
            return food

    def get_specific_food(self, name):
        return self.food_list[name]

    def get_specific_weapon(self, name):
        return self.weapons_list[name]

