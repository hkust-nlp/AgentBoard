from .utils import get_asset_path, render_from_layout

import matplotlib.pyplot as plt
import numpy as np

NUM_OBJECTS = 9
EMPTY, TILE1, TILE2, TILE3, TILE4, TILE5, TILE6, TILE7, TILE8 = range(NUM_OBJECTS)

def generate_tile_token(tile_num):
    if tile_num is None:
        return plt.imread(get_asset_path('slidetile_empty.png'))
    return plt.imread(get_asset_path('slidetile_{}.png'.format(tile_num)))

TOKEN_IMAGES = {
    EMPTY : generate_tile_token(None),
    TILE1 : generate_tile_token(1),
    TILE2 : generate_tile_token(2),
    TILE3 : generate_tile_token(3),
    TILE4 : generate_tile_token(4),
    TILE5 : generate_tile_token(5),
    TILE6 : generate_tile_token(6),
    TILE7 : generate_tile_token(7),
    TILE8 : generate_tile_token(8),
}


def build_layout(obs):
    layout = EMPTY * np.ones((3, 3), dtype=int)

    for lit in obs:
        if lit.predicate.name == 'at':
            tile, x, y = lit.variables
            assert tile.startswith("t")
            tile_num = int(tile[1:])
            assert x.startswith("x")
            c = int(x[1:]) - 1
            assert y.startswith("y")
            r = int(y[1:]) - 1
            layout[r, c] = tile_num

    return layout

def get_token_images(obs_cell):
    return [TOKEN_IMAGES[obs_cell]]

def render(obs, mode='human', close=False):
    layout = build_layout(obs)
    return render_from_layout(layout, get_token_images)
