from .utils import get_asset_path, render_from_layout, render_from_layout_crisp

import matplotlib.pyplot as plt
import numpy as np

NUM_OBJECTS = 6
CLEAR, PLAYER, STONE, STONE_AT_GOAL, GOAL, WALL = range(NUM_OBJECTS)

TOKEN_IMAGES = {
    PLAYER : plt.imread(get_asset_path('sokoban_player.png')),
    STONE : plt.imread(get_asset_path('sokoban_stone.png')),
    STONE_AT_GOAL : plt.imread(get_asset_path('sokoban_stone_at_goal.png')),
    GOAL : plt.imread(get_asset_path('sokoban_goal.png')),
    WALL : plt.imread(get_asset_path('sokoban_wall.png')),
    CLEAR : plt.imread(get_asset_path('sokoban_clear.png')),
}

def loc_str_to_loc(loc_str):
    _, r, c = loc_str.split('-')
    return (int(r), int(c))

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

def build_layout(obs):
    # Get location boundaries
    max_r, max_c = -np.inf, -np.inf
    for lit in obs:
        for v in lit.variables:
            if v.startswith('pos-'):
                r, c = loc_str_to_loc(v)
                max_r = max(max_r, r)
                max_c = max(max_c, c)
    layout = CLEAR * np.ones((max_r+1, max_c+1), dtype=np.uint8)

    # Put things in the layout
    # Also track seen locs and goal locs
    seen_locs = set()
    goal_locs = set()

    for v in get_values(obs, 'is-goal'):
        r, c = loc_str_to_loc(v[0])
        layout[r, c] = GOAL
        seen_locs.add((r, c))
        goal_locs.add((r, c))

    for r, c in get_locations(obs, 'stone'):
        if (r, c) in goal_locs:
            layout[r, c] = STONE_AT_GOAL
        else:
            layout[r, c] = STONE
        seen_locs.add((r, c))

    for r, c in get_locations(obs, 'player'):
        layout[r, c] = PLAYER
        seen_locs.add((r, c))

    for v in get_values(obs, 'clear'):
        r, c = loc_str_to_loc(v[0])
        if (r, c) in goal_locs:
            continue
        layout[r, c] = CLEAR
        seen_locs.add((r, c))

    # Add walls
    for v in get_values(obs, 'is-nongoal'):
        r, c = loc_str_to_loc(v[0])
        if (r, c) in seen_locs:
            continue
        layout[r, c] = WALL

    # 1 indexing
    layout = layout[1:, 1:]

    # r-c flip
    layout = np.transpose(layout)

    # print("layout:")
    # print(layout)
    # import ipdb; ipdb.set_trace()
    return layout

def build_layout_egocentric(obs,size=5):
    if (size % 2) == 0:
        size += 1
    width = (size-1)//2

    layout = CLEAR * np.ones((size, size), dtype=np.uint8)

    # Put things in the layout
    # Also track seen locs and goal locs
    seen_locs = set()
    goal_locs = set()

    for r, c in get_locations(obs, 'player'):
        player_r, player_c = r, c
        offset_r, offset_c = r - width, c - width

    def within_view(r,c):
        return (abs(r - player_r) <= width) and (abs(c - player_c) <= width)

    for v in get_values(obs, 'is-goal'):
        r, c = loc_str_to_loc(v[0])
        if within_view(r,c):
            layout[r-offset_r, c-offset_c] = GOAL
            seen_locs.add((r, c))
            goal_locs.add((r, c))

    for r, c in get_locations(obs, 'stone'):
        if within_view(r,c):
            if (r, c) in goal_locs:
                layout[r-offset_r, c-offset_c] = STONE_AT_GOAL
            else:
                layout[r-offset_r, c-offset_c] = STONE
            seen_locs.add((r, c))

    for r, c in get_locations(obs, 'player'):
        layout[width, width] = PLAYER
        seen_locs.add((r, c))

    for v in get_values(obs, 'clear'):
        r, c = loc_str_to_loc(v[0])
        if within_view(r,c):
            if (r, c) in goal_locs:
                continue
            layout[r-offset_r, c-offset_c] = CLEAR
            seen_locs.add((r, c))

    # Add walls
    for v in get_values(obs, 'is-nongoal'):
        r, c = loc_str_to_loc(v[0])
        if within_view(r,c):
            if (r, c) in seen_locs:
                continue
            layout[r-offset_r, c-offset_c] = WALL

    # r-c flip
    layout = np.transpose(layout)

    # print("layout:")
    # print(layout)
    # import ipdb; ipdb.set_trace()
    return layout

def get_token_images(obs_cell):
    return [TOKEN_IMAGES[obs_cell]]

def render(obs, mode='human', close=False):
    if mode == "egocentric":
        layout = build_layout_egocentric(obs)
        return render_from_layout(layout, get_token_images)
    elif mode == "human":
        layout = build_layout(obs)
        return render_from_layout(layout, get_token_images)
    elif mode == "egocentric_crisp":
        layout = build_layout_egocentric(obs)
        return render_from_layout_crisp(layout, get_token_images)
    elif mode == "human_crisp":
        layout = build_layout(obs)
        return render_from_layout_crisp(layout, get_token_images)
    elif mode == "layout":
        return build_layout(obs)
    elif mode == "egocentric_layout":
        return build_layout_egocentric(obs)
