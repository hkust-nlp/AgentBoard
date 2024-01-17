import numpy as np

NUM_OBJECTS = 7
BG, ROBOT, PERSON, WALL, HOSPITAL, ROBOT_HOLDING_PERSON, CHICKEN = range(NUM_OBJECTS)

COLORS = {
    BG : (0, 0, 0),
    ROBOT : (10, 150, 210),
    PERSON : (210, 50, 10),
    ROBOT_HOLDING_PERSON : (250, 150, 210),
    HOSPITAL : (10, 210, 50),
    WALL : (100, 100, 100),
    CHICKEN : (52, 102, 30),
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
            layout[r+min_r, c+min_c, ROBOT_HOLDING_PERSON] = 1
        else:
            layout[r+min_r, c+min_c, ROBOT] = 1

    for _, (r, c) in get_locations(obs, 'wall'):
        layout[r+min_r, c+min_c, WALL] = 1

    for _, (r, c) in get_locations(obs, 'hospital'):
        layout[r+min_r, c+min_c, HOSPITAL] = 1

    for _, (r, c) in get_locations(obs, 'person'):
        layout[r+min_r, c+min_c, PERSON] = 1

    return layout

def get_cell_color(obs_cell):
    for token in [ROBOT_HOLDING_PERSON, ROBOT, HOSPITAL, WALL, PERSON]:
        if obs_cell[token]:
            return COLORS[token]
    return COLORS[BG]

def render(obs, mode='human', close=False):
    layout = build_layout(obs)
    grid = np.zeros(layout.shape[:2] + (3,), dtype=np.uint8)
    for r in range(layout.shape[0]):
        for c in range(layout.shape[1]):
            grid[r, c] = get_cell_color(layout[r, c])
    scale = 10
    grid = grid.repeat(scale, axis=0).repeat(scale, axis=1)
    return grid
