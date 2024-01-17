from .utils import get_asset_path, render_from_layout

import matplotlib.pyplot as plt
import numpy as np

NUM_OBJECTS = 6
ROBOT, ROBOT_WITH_XRAY, PERSON, HIDDEN, WALL, FIRE = range(NUM_OBJECTS)

TOKEN_IMAGES = {
    ROBOT : plt.imread(get_asset_path('sar_robot.png')),
    ROBOT_WITH_XRAY : plt.imread(get_asset_path('sar_robot_xray.png')),
    PERSON : plt.imread(get_asset_path('sar_person.png')),
    HIDDEN : plt.imread(get_asset_path('sar_hidden.png')),
    WALL : plt.imread(get_asset_path('sar_wall.png')),
    FIRE : plt.imread(get_asset_path('sar_fire.png')),
}

def build_layout(obs, env):
    obs = dict(obs)
    # Get location boundaries
    min_r, min_c, max_r, max_c = 0, 0, env.height-1, env.width-1
    layout = np.zeros((max_r+1-min_r, max_c+1-min_c, NUM_OBJECTS), dtype=bool)

    # Put things in the layout
    r, c = obs["robot"]
    if obs.get("xray", False):
        layout[r, c, ROBOT_WITH_XRAY] = True
    else:
        layout[r, c, ROBOT] = True

    # Put in rooms
    for room_id, (r, c) in enumerate(env.room_locs):
        room_obs = obs[f"room{room_id}"]
        if room_obs == "person":
            layout[r, c, PERSON] = True
        elif room_obs == "?":
            layout[r, c, HIDDEN] = True

    # Put in walls
    for (r, c) in env.wall_locs:
        layout[r, c, WALL] = True

    # Put in fire
    for (r, c) in env.fire_locs:
        layout[r, c, FIRE] = True

    return layout

def get_token_images(obs_cell):
    images = []
    for token in [FIRE, ROBOT, ROBOT_WITH_XRAY, PERSON, HIDDEN, WALL]:
        if obs_cell[token]:
            images.append(TOKEN_IMAGES[token])
    return images

def render(obs, env, mode='human', close=False):
    layout = build_layout(obs, env)
    return render_from_layout(layout, get_token_images, dpi=150)
