from .utils import get_asset_path, render_from_layout

import matplotlib.pyplot as plt
import numpy as np

NUM_OBJECTS = 4
ROBOT, PERSON, WALL, FIRE = range(NUM_OBJECTS)

TOKEN_IMAGES = {
    ROBOT : plt.imread(get_asset_path('sar_robot.png')),
    PERSON : plt.imread(get_asset_path('sar_person.png')),
    WALL : plt.imread(get_asset_path('sar_wall.png')),
    FIRE : plt.imread(get_asset_path('sar_fire.png')),
}

def get_token_images(obs_cell):
    images = []
    for token in TOKEN_IMAGES:
        if obs_cell[token]:
            images.append(TOKEN_IMAGES[token])
    return images

def sar_render_from_string_grid(grid):
    layout = np.zeros((grid.shape[0], grid.shape[1], NUM_OBJECTS), dtype=bool)
    layout[grid == 'robot', ROBOT] = True
    layout[grid == 'person', PERSON] = True
    layout[grid == 'wall', WALL] = True
    layout[grid == 'fire', FIRE] = True
    return render_from_layout(layout, get_token_images, dpi=150)
