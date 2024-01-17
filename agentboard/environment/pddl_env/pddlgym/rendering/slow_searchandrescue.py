from .utils import get_asset_path, render_from_layout

import matplotlib.pyplot as plt
import numpy as np

NUM_OBJECTS = 6
ROBOT, PERSON, WALL, HOSPITAL, ROBOT_HOLDING_PERSON, CHICKEN = range(NUM_OBJECTS)

TOKEN_IMAGES = {
    ROBOT : plt.imread(get_asset_path('sar_robot.png')),
    PERSON : plt.imread(get_asset_path('sar_person.png')),
    WALL : plt.imread(get_asset_path('sar_wall.png')),
    HOSPITAL : plt.imread(get_asset_path('sar_hospital.png')),
    ROBOT_HOLDING_PERSON : plt.imread(get_asset_path('sar_robot_holding_person.png')),
    CHICKEN : plt.imread(get_asset_path('sar_chicken.png')),
}

def loc_str_to_loc(loc_str):
    assert loc_str.startswith("f") and loc_str.endswith("f")
    r, c = loc_str[1:-1].split('-')
    return (int(r), int(c))

def get_locations(obs, thing):
    locs = []
    for lit in obs:
        if '-at' not in lit.predicate.name:
            continue
        if thing in lit.variables[0]:
            loc = loc_str_to_loc(lit.variables[1])
            locs.append((lit.variables[0], loc))
    return locs

def robot_is_carrying(robot, obs):
    for lit in obs:
        if lit.predicate.name == "handsfree" and lit.variables[0] == robot:
            return False
    return True

def build_layout(obs):
    # Get location boundaries
    min_r, min_c, max_r, max_c = np.inf, np.inf, -np.inf, -np.inf
    for lit in obs:
        for v in lit.variables:
            if v.startswith('f') and v.endswith('f'):
                r, c = loc_str_to_loc(v)
                max_r = max(max_r, r)
                max_c = max(max_c, c)
                min_r = min(min_r, r)
                min_c = min(min_c, c)
    layout = np.zeros((max_r+1-min_r, max_c+1-min_c, NUM_OBJECTS), dtype=bool)

    # Put things in the layout
    for robot, (r, c) in get_locations(obs, 'robot'):
        if robot_is_carrying(robot, obs):
            layout[r, c, ROBOT_HOLDING_PERSON] = 1
        else:
            layout[r, c, ROBOT] = 1

    for _, (r, c) in get_locations(obs, 'wall'):
        layout[r, c, WALL] = 1

    for _, (r, c) in get_locations(obs, 'hospital'):
        layout[r, c, HOSPITAL] = 1

    for _, (r, c) in get_locations(obs, 'person'):
        layout[r, c, PERSON] = 1

    for _, (r, c) in get_locations(obs, 'chicken'):
        layout[r, c, CHICKEN] = 1

    return layout

def get_token_images(obs_cell):
    images = []
    for token in [HOSPITAL, WALL, ROBOT_HOLDING_PERSON, ROBOT, PERSON, CHICKEN]:
        if obs_cell[token]:
            images.append(TOKEN_IMAGES[token])
    return images

def render(obs, mode='human', close=False):
    layout = build_layout(obs)
    return render_from_layout(layout, get_token_images, dpi=150)
