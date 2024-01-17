from .utils import get_asset_path, render_from_layout

import matplotlib.pyplot as plt
import numpy as np

NUM_OBJECTS = 10
GOAL_UP_PLAYER, GOAL_LEFT_PLAYER, GOAL_DOWN_PLAYER, GOAL_RIGHT_PLAYER, NOT_GOAL_UP_PLAYER, NOT_GOAL_LEFT_PLAYER, NOT_GOAL_DOWN_PLAYER, NOT_GOAL_RIGHT_PLAYER, WALL, PERSON = range(NUM_OBJECTS)

TOKEN_IMAGES = {
    GOAL_UP_PLAYER: plt.imread(get_asset_path('sar_robot_holding_person.png')),
    GOAL_LEFT_PLAYER: np.rot90(plt.imread(get_asset_path('sar_robot_holding_person.png')), k = 1),
    GOAL_DOWN_PLAYER: np.rot90(plt.imread(get_asset_path('sar_robot_holding_person.png')), k = 2),
    GOAL_RIGHT_PLAYER: np.rot90(plt.imread(get_asset_path('sar_robot_holding_person.png')), k = 3),
    NOT_GOAL_UP_PLAYER: plt.imread(get_asset_path('sar_robot.png')),
    NOT_GOAL_LEFT_PLAYER: np.rot90(plt.imread(get_asset_path('sar_robot.png')), k = 1),
    NOT_GOAL_DOWN_PLAYER: np.rot90(plt.imread(get_asset_path('sar_robot.png')), k = 2),
    NOT_GOAL_RIGHT_PLAYER: np.rot90(plt.imread(get_asset_path('sar_robot.png')), k = 3),
    WALL : plt.imread(get_asset_path('sar_wall.png')),
    PERSON : plt.imread(get_asset_path('sar_person.png')),
}

def get_token_images(obs_cell):
    images = []
    for token in TOKEN_IMAGES:
        if obs_cell[token]:
            images.append(TOKEN_IMAGES[token])
    return images

def maze_render_from_string_grid(grid):
    layout = np.zeros((grid.shape[0], grid.shape[1], NUM_OBJECTS), dtype=bool)
    layout[grid == 'goal_up_player', GOAL_UP_PLAYER] = True
    layout[grid == 'goal_left_player', GOAL_LEFT_PLAYER] = True
    layout[grid == 'goal_down_player', GOAL_DOWN_PLAYER] = True
    layout[grid == 'goal_right_player', GOAL_RIGHT_PLAYER] = True
    layout[grid == 'not_goal_up_player', NOT_GOAL_UP_PLAYER] = True
    layout[grid == 'not_goal_left_player', NOT_GOAL_LEFT_PLAYER] = True
    layout[grid == 'not_goal_down_player', NOT_GOAL_DOWN_PLAYER] = True
    layout[grid == 'not_goal_right_player', NOT_GOAL_RIGHT_PLAYER] = True
    layout[grid == 'wall', WALL] = True
    layout[grid == 'goal', PERSON] = True
    return render_from_layout(layout, get_token_images, dpi=150)

#TODO: Possible bug because we only show clear and not walls, therefore may have incorrect bounds
def build_string_grid(obs):
    num_rows, num_cols = 0, 0
    orientation = None
    player_loc = None
    clear_locs = set()
    goal_loc = None
    for lit in obs:
        for var in lit.variables:
            if var.startswith('loc-'):
                row, col = loc_str_to_loc(var)
                num_rows = max(num_rows, row)
                num_cols = max(num_cols, col)

        if lit.predicate.name.startswith("oriented"):
            orientation = lit.predicate.name[9:]
        elif lit.predicate.name.startswith("at"): #Player
            player_loc = loc_str_to_loc(lit.variables[1])
        elif lit.predicate.name.startswith("clear"): #Clear
            clear_locs.add(loc_str_to_loc(lit.variables[0]))
        elif lit.predicate.name.startswith("is-goal"): #Is Goal
            goal_loc = loc_str_to_loc(lit.variables[0])

    #To account for rightmost and lowest walls which do not have a literal in obs
    num_rows += 1 
    num_cols += 1

    grid = [["wall" for _ in range(num_cols)] for _ in range(num_rows)] #All are walls unless clear or player or goal

    if player_loc == goal_loc: #If player at goal
        grid[goal_loc[0]-1][goal_loc[1]-1] = "goal_" + orientation + "_player"
    else:
        grid[goal_loc[0]-1][goal_loc[1]-1] = "goal"
        grid[player_loc[0]-1][player_loc[1]-1] = "not_goal_" + orientation + "_player"

    for row, col in clear_locs:
        if (row, col) != goal_loc:
            grid[row-1][col-1] = "clear"
    
    return np.array(grid)

def render(obs):
    return maze_render_from_string_grid(build_string_grid(obs))

#Taken from searchandrescue.py
def loc_str_to_loc(loc_str):
    _, r, c = loc_str.split(':')[0].split('-')
    return (int(r), int(c)) 
