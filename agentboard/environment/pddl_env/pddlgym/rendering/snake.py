import numpy as np

def parse_position(pos):
    assert pos.startswith("pos")
    xs, ys = pos[3:].split("-")
    return int(xs), int(ys)

def render(state_literals, *args, **kwargs):

    colors = {
        'empty' : (0, 0, 0),
        'snake' : (10, 240, 10),
        'obstacle' : (100, 100, 100),
        'food' : (240, 240, 240),
    }

    # get all positions
    min_x, min_y, max_x, max_y = np.inf, np.inf, -np.inf, -np.inf
    for lit in state_literals:
        if lit.predicate.name == "isadjacent":
            for pos in lit.variables:
                x, y = parse_position(pos)
                min_x = min(x, min_x)
                min_y = min(y, min_y)
                max_x = max(x, max_x)
                max_y = max(y, max_y)

    # find snake positions
    snake_positions = set()
    for lit in state_literals:
        if lit.predicate.name == "nextsnake":
            for pos in lit.variables:
                x, y = parse_position(pos)
                snake_positions.add((x, y))

    # find obstacle positions
    obstacle_positions = set()
    for lit in state_literals:
        if lit.predicate.name == "blocked":
            x, y = parse_position(lit.variables[0])
            if (x, y) not in snake_positions:
                obstacle_positions.add((x, y))


    # food
    food_positions = set()
    for lit in state_literals:
        if lit.predicate.name == "ispoint":
            x, y = parse_position(lit.variables[0])
            food_positions.add((x, y))

    # create a grid
    grid = np.zeros((max_x - min_x + 1, max_y - min_y + 1, 3), dtype=np.uint8)
    grid[:, :] = colors['empty']

    for x, y in snake_positions:
        grid[x-min_x, y-min_y] = colors['snake']
    for x, y in obstacle_positions:
        grid[x-min_x, y-min_y] = colors['obstacle']
    for x, y in food_positions:
        grid[x-min_x, y-min_y] = colors['food']

    scale = 20
    grid = grid.repeat(scale, axis=0).repeat(scale, axis=1)

    return grid

