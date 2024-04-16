import random
from food import Food


class ObjectSpawner:
    """This class is responsible for spawning food and weapons in the game"""

    def __init__(self, row_lenght, column_lenght):

        self.total_amount_of_cells = row_lenght * column_lenght
        self.cell_probability = 1 / self.total_amount_of_cells
        self.grid = [
            [self.cell_probability for x in range(row_lenght)] for y in range(column_lenght)]

        self.food_list = []
        self.weapons_list = []

    def set_specific_chance_in_grid(self, grid_x, grid_y, chance):
        self.grid[grid_x][grid_y] = chance

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
        for interator in range(len(cum_sums)):

            row_total = 0

            for j in range(len(cum_sums[interator])):
                row_total += cum_sums[interator][j]
            cum_row_probs.append(row_total)

        rand_row = random.choices(
            range(len(cum_row_probs)), weights=cum_row_probs)
        rand_col = 0
        rand_num = random.uniform(0, 1)

        for interator, cum_prob in enumerate(cum_probs[rand_row[0]]):
            if rand_num < cum_prob:
                rand_col = interator
                break

        return rand_row[0], rand_col

    def choose_all_spawn_cells_based_on_given_probability(self, probability: float):
        list_of_cells = []
        for row in range(len(self.grid)):
            for column in range(len(self.grid[row])):
                rand_num = random.uniform(0, 1)
                if rand_num < probability:
                    list_of_cells.append(self.grid[row][column])
        return list_of_cells

    def spawn_food(self, grid):
        grid_x, grid_y = self.choose_spawn_cell()
        if not grid[grid_x][grid_y].objects:
            food = Food(grid[grid_x][grid_y].x, grid[grid_x]
                        [grid_y].y, 30 // 2, (0, 255, 0), True)
            grid[grid_x][grid_y].objects.append(food)
            return food

    def get_specific_food(self, name):
        return self.food_list[name]

    def get_specific_weapon(self, name):
        return self.weapons_list[name]
