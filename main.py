import sys
import pygame
import agent
from Sectors.gridsection import Grid

# Initialize Pygame
pygame.init()

# Set up clock
clock = pygame.time.Clock()
FPS = 60

# Set screen dimensions
screen_width, screen_height = 500, 500
screen = pygame.display.set_mode((screen_width, screen_height))

# Set cell dimensions
cell_size = 50
num_rows = screen_height // cell_size
num_cols = screen_width // cell_size

# Create 2D array to hold grid cells
grid_list = [[Grid(name=f"Row {i}, Comlumm {j}",x=i*cell_size+25,y=j*cell_size+25,cellsize=cell_size) for j in range(num_cols)] for i in range(num_rows)]

# Set up colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Draw grid outlines
def render_grid(cell_size, num_rows, num_cols):
    for i in range(num_rows):
        for j in range(num_cols):
            rect = pygame.Rect(j*cell_size, i*cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, WHITE, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

# Call grid to draw a dot in the center of each cell
def call_grid():
    for i in range(num_rows):
        for j in range(num_cols):
            #print(grid[i][j].get_name())
            grid_list[i][j].draw(screen)
    pass
# Create agent
agent = agent.Agent((50, 50))

# Run event loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        agent.manual_move(event)

    render_grid(cell_size, num_rows, num_cols)
    call_grid()
    agent.move(grid_list)
    #agent.draw(screen)
    pygame.display.update()
    clock.tick(FPS)