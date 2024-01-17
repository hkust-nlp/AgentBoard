from .utils import get_asset_path, render_from_layout_crisp

import matplotlib.pyplot as plt
import numpy as np

NUM_OBJECTS = 10
ROCK, PATH, GOAL, WATER, HILL, PLAYER_ROCK, PLAYER_PATH, PLAYER_GOAL, PLAYER_WATER, PLAYER_HILL = range(10)

TOKEN_IMAGES = {
    ROCK : plt.imread(get_asset_path('hiking_rock.png')),
    PATH : plt.imread(get_asset_path('hiking_path.png')),
    GOAL : plt.imread(get_asset_path('hiking_goal.png')),
    WATER : plt.imread(get_asset_path('hiking_water.png')),
    HILL : plt.imread(get_asset_path('hiking_hill.png')),

    PLAYER_ROCK : plt.imread(get_asset_path('hiking_player_on_rock.png')),
    PLAYER_PATH : plt.imread(get_asset_path('hiking_player_on_path.png')),
    PLAYER_GOAL : plt.imread(get_asset_path('hiking_player_on_goal.png')),
    PLAYER_WATER : plt.imread(get_asset_path('hiking_player_on_water.png')),
    PLAYER_HILL : plt.imread(get_asset_path('hiking_player_on_hill.png')),

}

def loc_str_to_loc(loc_str):
    rs, cs = loc_str.split('_')
    assert rs[0] == 'r'
    assert cs[0] == 'c'
    return (int(rs[1:]), int(cs[1:]))

def get_values(obs, name):
    values = []
    for lit in obs:
        if lit.predicate.name == name:
            if len(lit.variables) == 1:
                values.append(loc_str_to_loc(lit.variables[0]))
            else:
                values.append(tuple(map(loc_str_to_loc, lit.variables)))
    return values

def build_layout(obs):
    # Get location boundaries
    max_r, max_c = -np.inf, -np.inf
    for lit in obs:
        for v in lit.variables:
            r, c = loc_str_to_loc(v)
            max_r = max(max_r, r)
            max_c = max(max_c, c)
    layout = ROCK * np.ones((max_r+1, max_c+1), dtype=np.uint8)

    # Put things in the layout
    current_locs = get_values(obs, 'at')
    assert len(current_locs) == 1
    player_r, player_c = current_locs[0]
    layout[player_r, player_c] = PLAYER_ROCK  # may get overwritten below

    for ((r, c), _) in get_values(obs, 'ontrail'):
        if (r, c) == (player_r, player_c):
            layout[r, c] = PLAYER_PATH
        else:
            layout[r, c] = PATH

    for r, c in get_values(obs, 'iswater'):
        if (r, c) == (player_r, player_c):
            layout[r, c] = PLAYER_WATER
        else:
            layout[r, c] = WATER

    for r, c in get_values(obs, 'ishill'):
        if (r, c) == (player_r, player_c):
            layout[r, c] = PLAYER_HILL
        else:
            layout[r, c] = HILL

    for r, c in get_values(obs, 'isgoal'):
        if (r, c) == (player_r, player_c):
            layout[r, c] = PLAYER_GOAL
        else:
            layout[r, c] = GOAL

    return layout

def get_token_images(obs_cell):
    return [TOKEN_IMAGES[obs_cell]]

def render(obs, mode='human', close=False):
    layout = build_layout(obs)
    return render_from_layout_crisp(layout, get_token_images, tilesize=64)
