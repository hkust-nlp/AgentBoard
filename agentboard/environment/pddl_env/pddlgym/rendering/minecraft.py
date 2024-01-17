from .utils import get_asset_path, render_from_layout

import matplotlib.pyplot as plt
import numpy as np

NUM_OBJECTS = 6
AGENT, LOG, PLANK, GRASS, FRAME, BACKGROUND = range(NUM_OBJECTS)

TOKEN_IMAGES = {
    AGENT : plt.imread(get_asset_path('minecraft_agent.png')),
    LOG : plt.imread(get_asset_path('minecraft_log.jpg')),
    PLANK : plt.imread(get_asset_path('minecraft_plank.png')),
    GRASS : plt.imread(get_asset_path('minecraft_grass.jpg')),
    FRAME : plt.imread(get_asset_path('minecraft_frame.png')),
    BACKGROUND : plt.imread(get_asset_path('minecraft_background.png')),
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
        if thing == 'agent':
            if lit.predicate.name == "agentat":
                locs.append(loc_str_to_loc(lit.variables[0]))
        elif lit.predicate.name != 'at':
            continue
        elif lit.variables[0].startswith(thing):
            locs.append(loc_str_to_loc(lit.variables[1]))
    return locs

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
    layout[..., BACKGROUND] = 1

    # Put things in the layout
    agent_loc = get_locations(obs, 'agent')[0]
    layout[agent_loc[0], agent_loc[1], AGENT] = 1

    for thing, thing_type in zip(
        ['log', 'grass'],
        [LOG, GRASS]):
        locs = get_locations(obs, thing)
        for loc in locs:
            r, c = loc
            layout[r, c, thing_type] = 1

    inventory_layout = np.zeros((layout.shape[0], 1, NUM_OBJECTS))
    next_inventory_r = 0

    for lit in obs:
        if lit.predicate.name == "inventory":
            if lit.variables[0].startswith("log"):
                thing_type = LOG
            elif lit.variables[0].startswith("grass"):
                thing_type = GRASS
            elif lit.variables[0].startswith("new"):
                thing_type = PLANK
            else:
                import ipdb; ipdb.set_trace()

            inventory_layout[next_inventory_r, 0, thing_type] = 1
            next_inventory_r += 1
            if next_inventory_r > inventory_layout.shape[0] - 1:
                break

    final_layout = np.zeros((layout.shape[0] + 2, layout.shape[1] + 4, NUM_OBJECTS))
    final_layout[0, :, FRAME] = 1
    final_layout[-1, :, FRAME] = 1
    final_layout[:, 0, FRAME] = 1
    final_layout[:, -1, FRAME] = 1
    final_layout[:, -3, FRAME] = 1
    final_layout[1:-1, 1:-3] = layout
    final_layout[1:-1, -2:-1] = inventory_layout

    return final_layout

def get_token_images(obs_cell):
    if obs_cell[BACKGROUND]:
        yield TOKEN_IMAGES[BACKGROUND]
    if obs_cell[FRAME]:
        yield TOKEN_IMAGES[FRAME]
    if obs_cell[GRASS]:
        yield TOKEN_IMAGES[GRASS]
    if obs_cell[LOG]:
        yield TOKEN_IMAGES[LOG]
    if obs_cell[PLANK]:
        yield TOKEN_IMAGES[PLANK]
    if obs_cell[AGENT]:
        yield TOKEN_IMAGES[AGENT]
    return

def render(obs, mode='human', close=False):
    layout = build_layout(obs)
    return render_from_layout(layout, get_token_images)
