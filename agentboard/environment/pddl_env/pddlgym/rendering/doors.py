from .utils import get_asset_path, render_from_layout

from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np


NUM_OBJECTS = 5
PLAYER, LOCKED_ROOM, UNLOCKED_ROOM, KEY, BOUNDARY = range(NUM_OBJECTS)

TOKEN_IMAGES = {
    PLAYER : plt.imread(get_asset_path('doors_player.png')),
    LOCKED_ROOM : plt.imread(get_asset_path('doors_locked_room.png')),
    UNLOCKED_ROOM : plt.imread(get_asset_path('doors_unlocked_room.png')),
    BOUNDARY : plt.imread(get_asset_path('doors_boundary.png')),
    KEY : plt.imread(get_asset_path('doors_key.png')),
}

def loc_str_to_loc(loc_str):
    split = loc_str.split("-")
    assert split[0] == 'loc' and len(split) == 3
    return (int(split[1]), int(split[2]))

def get_player_loc(obs):
    locs = []
    for lit in obs:
        if lit.predicate.name.lower() == 'at':
            return loc_str_to_loc(lit.variables[0])
    raise Exception("player not found in obs (no at literal)")

def get_key_locs(obs):
    locs = []
    for lit in obs:
        if lit.predicate.name.lower() == 'keyat':
            yield loc_str_to_loc(lit.variables[1])

def get_rooms(obs):
    rooms_to_locs = defaultdict(set)
    loc_to_room = {}
    unlocked_rooms = set()

    for lit in obs:
        if lit.predicate.name.lower() == "unlocked":
            unlocked_rooms.add(lit.variables[0])
        if lit.predicate.name.lower() == "locinroom":
            loc = loc_str_to_loc(lit.variables[0])
            room = lit.variables[1]
            rooms_to_locs[room].add(loc)
            loc_to_room[loc] = room

    return rooms_to_locs, loc_to_room, unlocked_rooms


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
    player_loc = get_player_loc(obs)
    layout[player_loc[0], player_loc[1], PLAYER] = 1

    # Keys
    key_locs = get_key_locs(obs)
    for key_loc in key_locs:
        layout[key_loc[0], key_loc[1], KEY] = 1

    # Rooms
    rooms_to_locs, loc_to_room, unlocked_rooms = get_rooms(obs)
    for room in rooms_to_locs:
        unlocked = room in unlocked_rooms
        for loc in rooms_to_locs[room]:
            if unlocked:
                layout[loc[0], loc[1], UNLOCKED_ROOM] = 1
            else:
                layout[loc[0], loc[1], LOCKED_ROOM] = 1

    # Add boundaries between rooms
    for r in range(layout.shape[0]):
        for c in range(layout.shape[1]):
            room = loc_to_room[r, c]

            if room in unlocked_rooms:
                continue

            # Check for neighboring rooms

            # Boundary above
            if r == 0 or loc_to_room[(r-1, c)] != room:
                layout[r, c, BOUNDARY] = 1
            # Boundary left
            if c == 0 or loc_to_room[(r, c-1)] != room:
                layout[r, c, BOUNDARY] = 1
            # Boundary below
            if r == layout.shape[0]-1 or loc_to_room[(r+1, c)] != room:
                layout[r, c, BOUNDARY] = 1
            # Boundary right
            if c == layout.shape[1]-1 or loc_to_room[(r, c+1)] != room:
                layout[r, c, BOUNDARY] = 1

    return layout

def get_token_images(obs_cell):
    if obs_cell[LOCKED_ROOM]:
        yield TOKEN_IMAGES[LOCKED_ROOM]
    if obs_cell[UNLOCKED_ROOM]:
        yield TOKEN_IMAGES[UNLOCKED_ROOM]
    if obs_cell[BOUNDARY]:
        yield TOKEN_IMAGES[BOUNDARY]
    if obs_cell[PLAYER]:
        yield TOKEN_IMAGES[PLAYER]
    if obs_cell[KEY]:
        yield TOKEN_IMAGES[KEY]
    return

def render(obs, mode='human', close=False):
    layout = build_layout(obs)
    return render_from_layout(layout, get_token_images)
