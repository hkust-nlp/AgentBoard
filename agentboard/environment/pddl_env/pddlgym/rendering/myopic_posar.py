from .utils import get_asset_path, render_from_layout

import matplotlib.pyplot as plt
import numpy as np

NUM_OBJECTS = 6
ROBOT, PERSON, SMOKE, FIRE, WALL, EMPTY = range(NUM_OBJECTS)

TOKEN_IMAGES = {
    ROBOT : plt.imread(get_asset_path('sar_robot.png')),
    PERSON : plt.imread(get_asset_path('sar_person.png')),
    SMOKE : plt.imread(get_asset_path('sar_smoke.png')),
    FIRE : plt.imread(get_asset_path('sar_fire.png')),
    WALL : plt.imread(get_asset_path('sar_wall.png')),
}

def build_layout(obs, env):
    obs = dict(obs)
    # Get location boundaries
    min_r, min_c, max_r, max_c = 0, 0, env.height-1, env.width-1
    layout = np.zeros((max_r+1-min_r, max_c+1-min_c, NUM_OBJECTS), dtype=bool)

    # Put things in the layout
    r, c = obs["robot"]
    layout[r, c, ROBOT] = True

    if obs["cell"] == "person":
        layout[r, c, PERSON] = True

    if obs["smoke"]:
        layout[r, c, SMOKE] = True

    if obs["cell"] == "fire":
        layout[r, c, FIRE] = True

    # Color unknown cells gray
    grid_colors = np.full(layout.shape[:2], 'gray', dtype=object)
    grid_colors[r, c] = 'white'

    return layout, grid_colors

def get_token_images(obs_cell):
    images = []
    for token in [FIRE, ROBOT, SMOKE, PERSON, WALL]:
        if obs_cell[token]:
            images.append(TOKEN_IMAGES[token])
    return images

def render(obs, env, mode='human', close=False):
    layout, grid_colors = build_layout(obs, env)
    return render_from_layout(layout, get_token_images, dpi=150,
        grid_colors=grid_colors)

def posar_render_from_layout(layout):
    known_mask = np.any(layout, axis=2)
    grid_colors = np.full(layout.shape[:2], 'gray', dtype=object)
    grid_colors[known_mask] = 'white'
    return render_from_layout(layout, get_token_images, dpi=150,
        grid_colors=grid_colors)
