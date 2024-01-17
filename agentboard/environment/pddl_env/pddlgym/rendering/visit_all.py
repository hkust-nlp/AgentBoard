from .utils import get_asset_path, render_from_layout

import matplotlib.pyplot as plt
import numpy as np


NUM_OBJECTS = 3
ROBOT, LOCATION, TO_VISIT = range(NUM_OBJECTS)

TOKEN_IMAGES = {
    ROBOT : plt.imread(get_asset_path('sokoban_player.png')),
    LOCATION: plt.imread(get_asset_path('sokoban_clear.png')),
    TO_VISIT: plt.imread(get_asset_path('sokoban_goal.png')),
}

def get_robot_locations(obs):
    locs = []
    for lit in obs:
        if lit.predicate.name == 'at-robot':
            locs.append(loc_str_to_loc(lit.variables[0]))
    return locs

def get_values(obs, name):
    values = []
    for lit in obs:
        if lit.predicate.name == name:
            values.append(lit.variables)
    return values
def loc_str_to_loc(loc_str):
    _, r, c = loc_str.split('-')
    return (int(r[1::]), int(c[1::]))

def build_layout(obs):
    # Get location boundaries
    max_r, max_c = -np.inf, -np.inf # r - row; c - collumn
    for lit in obs:
        for v in lit.variables:
            if v.startswith('loc-'):
                r, c = loc_str_to_loc(v)
                max_r = max(max_r, r)
                max_c = max(max_c, c)
    layout = TO_VISIT * np.ones((max_r+1, max_c+1), dtype=np.uint8)


    # Put things in the layout
    # Also track visited locs
    visited_locs = set()

    for v in get_values(obs, 'visited'):
        r, c = loc_str_to_loc(v[0])
        layout[r, c] = LOCATION
        visited_locs.add((r, c))

    for r, c in get_robot_locations(obs) :
        layout[r, c] = ROBOT
        visited_locs.add((r, c))

    # 1 indexing
    # layout = layout[1:, 1:]

    # r-c flip
    layout = np.transpose(layout)

    # print("layout:", layout)
    # import ipdb; ipdb.set_trace()
    return layout


def get_token_images(obs_cell):
    return [TOKEN_IMAGES[obs_cell]]

def render(obs, mode='human', close=False):
    if mode == "human":
        layout = build_layout(obs)
        return render_from_layout(layout, get_token_images)