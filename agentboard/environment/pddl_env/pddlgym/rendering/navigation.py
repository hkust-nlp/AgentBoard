from .utils import get_asset_path, render_from_layout, render_from_layout_crisp
import pddlgym

import matplotlib.pyplot as plt
import numpy as np

NUM_OBJECTS = 3
ROBOT, PROB, GOAL = range(NUM_OBJECTS)

PROB_CELL = np.zeros((200, 200, 3), np.uint8)
PROB_CELL[:] = [244, 244, 244]

GOAL_CELL = np.zeros((200, 200, 3), np.uint8)
GOAL_CELL[:] = [24, 255, 42]

TOKEN_IMAGES = {
    ROBOT : plt.imread(get_asset_path('sokoban_player.png')),
    PROB : PROB_CELL,
    GOAL: GOAL_CELL
}

def loc_str_to_loc(loc_str):
    c, r = loc_str.split('-')
    return (int(r[:-1]), int(c[1:]))

def get_locations(obs, thing):
    locs = []
    for lit in obs:
        if lit.predicate.name != 'at':
            continue
        if thing in lit.variables[0]:
            locs.append(loc_str_to_loc(lit.variables[1]))
    return locs

def get_values(obs, name):
    values = []
    for lit in obs:
        if lit.predicate.name == name:
            values.append(lit.variables)
    return values

def build_layout(obs, domain):
    # Get location boundaries
    max_r, max_c = -np.inf, -np.inf
    for lit in obs:
        for v in lit.variables:
            if v.startswith('f'):
                r, c = loc_str_to_loc(v)
                max_r = max(max_r, r)
                max_c = max(max_c, c)
    layout = PROB * np.ones((max_r+1, max_c+1, 2), dtype=np.uint8)

    layout[:, :, 1] = 255
    # Put things in the layout
    # Also track seen locs and goal locs
    seen_locs = set()
    goal_locs = set()

    for v in get_values(obs, 'is-goal'):
        r, c = loc_str_to_loc(v[0])
        layout[r, c] = [GOAL, 255]
        seen_locs.add((r, c))
        goal_locs.add((r, c))

    for r, c in get_locations(obs, 'robot'):
        layout[r, c] = [ROBOT, 255]
        seen_locs.add((r, c))

    for v in get_values(obs, 'is-prob'):
        r, c = loc_str_to_loc(v[0])
        if (r, c) in goal_locs:
            continue
        def get_prob(col):
            operator = [
                op for name, op in domain.operators.items()
                if '-col-' in name and int(name.split('-')[-1]) == col][0]
            prob_effect = [
                lit for lit in operator.effects.literals
                if type(lit) == pddlgym.structs.ProbabilisticEffect][0]
            return prob_effect.probabilities[0]

        prob = get_prob(c)
        layout[r, c] = [PROB, prob * 255]
        seen_locs.add((r, c))

    for v in get_values(obs, 'robot-at'):
        r, c = loc_str_to_loc(v[0])
        layout[r, c] = [ROBOT, 255]
        seen_locs.add((r, c))

    return layout

def get_token_images(obs_cell):
    id_obs, factor = obs_cell
    arr = TOKEN_IMAGES[id_obs]
    arr_type = arr.dtype
    return [(arr * (factor / 255)).astype(arr_type)]

def render(obs, domain, close=False):
    layout = build_layout(obs, domain)
    return render_from_layout(layout, get_token_images)
