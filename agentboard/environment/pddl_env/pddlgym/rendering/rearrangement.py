from .utils import get_asset_path, render_from_layout

import matplotlib.pyplot as plt
import numpy as np

NUM_OBJECTS = 8
ROBOT, PAWN, BEAR, MONKEY, ROBOT_HOLDING_PAWN, ROBOT_HOLDING_BEAR, ROBOT_HOLDING_MONKEY, GOAL = range(NUM_OBJECTS)

TOKEN_IMAGES = {
    ROBOT : plt.imread(get_asset_path('robot.png')),
    PAWN : plt.imread(get_asset_path('pawn.png')),
    BEAR : plt.imread(get_asset_path('bear.png')),
    MONKEY : plt.imread(get_asset_path('monkey.png')),
    ROBOT_HOLDING_PAWN : plt.imread(get_asset_path('robot_holding_pawn.png')),
    ROBOT_HOLDING_BEAR : plt.imread(get_asset_path('robot_holding_bear.png')),
    ROBOT_HOLDING_MONKEY : plt.imread(get_asset_path('robot_holding_monkey.png')),
    GOAL : plt.imread(get_asset_path('goal.png')),
}

def loc_str_to_loc(loc_str):
    # assert len(loc_str) == 5
    # return (int(loc_str[3]), int(loc_str[4]))
    split = loc_str.split("-")
    assert split[0] == 'loc' and len(split) == 3
    return (int(split[1]), int(split[2]))

def get_locations(obs, thing):
    locs = []
    for lit in obs:
        if thing == 'goal':
            if lit.predicate.name == "isgoal":
                locs.append(loc_str_to_loc(lit.variables[0]))
        elif lit.predicate.name != 'at':
            continue
        if lit.variables[0].startswith(thing):
            locs.append(loc_str_to_loc(lit.variables[1]))
    return locs

def is_holding(obs, thing):
    for lit in obs:
        if lit.predicate.name != 'holding':
            continue
        if lit.variables[0] == thing:
            return True
    return False

def build_layout(obs):
    # Get location boundaries
    max_r, max_c = 2, 2
    for lit in obs:
        for v in lit.variables:
            if 'loc' in v:
                r, c = loc_str_to_loc(v)
                max_r = max(max_r, r)
                max_c = max(max_c, c)
    layout = np.zeros((max_r+1, max_c+1, NUM_OBJECTS))

    # Put things in the layout
    robot_loc = get_locations(obs, 'robot')[0]
    layout[robot_loc[0], robot_loc[1], ROBOT] = 1

    for thing, thing_type, holding_thing_type in zip(
        ['pawn', 'bear', 'monkey', 'goal'],
        [PAWN, BEAR, MONKEY, GOAL],
        [ROBOT_HOLDING_PAWN, ROBOT_HOLDING_BEAR, ROBOT_HOLDING_MONKEY, None]):
        locs = get_locations(obs, thing)
        for loc in locs:
            r, c = loc
            layout[r, c, thing_type] = 1
            if thing != 'goal' and is_holding(obs, thing):
                layout[r, c, holding_thing_type] = 1

    return layout

def get_token_images(obs_cell):
    if obs_cell[GOAL]:
        yield TOKEN_IMAGES[GOAL]
    if obs_cell[ROBOT]:
        yield TOKEN_IMAGES[ROBOT]
    if obs_cell[BEAR]:
        yield TOKEN_IMAGES[BEAR]
    if obs_cell[PAWN]:
        yield TOKEN_IMAGES[PAWN]
    if obs_cell[MONKEY]:
        yield TOKEN_IMAGES[MONKEY]
    if obs_cell[ROBOT_HOLDING_PAWN]:
        yield TOKEN_IMAGES[ROBOT_HOLDING_PAWN]
    if obs_cell[ROBOT_HOLDING_BEAR]:
        yield TOKEN_IMAGES[ROBOT_HOLDING_BEAR]
    if obs_cell[ROBOT_HOLDING_MONKEY]:
        yield TOKEN_IMAGES[ROBOT_HOLDING_MONKEY]
    return

def render(obs, mode='human', close=False):
    layout = build_layout(obs)
    return render_from_layout(layout, get_token_images)
