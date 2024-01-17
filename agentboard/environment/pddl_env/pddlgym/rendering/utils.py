from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import RegularPolygon
from PIL import Image

import matplotlib.pyplot as plt
import numpy as np
import os

IM_SCALE = 0.25

def get_asset_path(asset_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    asset_dir_path = os.path.join(dir_path, 'assets')
    return os.path.join(asset_dir_path, asset_name)

def fig2data(fig, dpi: int = 150):
    fig.set_dpi(dpi)
    fig.canvas.draw()

    # copy image data from buffer
    data = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8).copy()

    # get the dpi adjusted figure dimensions
    width, height = map(int, fig.get_size_inches() * fig.get_dpi())
    data = data.reshape(height, width, 4)
    
    data[..., [0, 1, 2, 3]] = data[..., [1, 2, 3, 0]]

    return data

def initialize_figure(height, width, fig_scale=1., grid_colors=None):
    fig = plt.figure(figsize=((width + 2) * fig_scale, (height + 2) * fig_scale))
    ax = fig.add_axes((0.0, 0.0, 1.0, 1.0),
                                aspect='equal', frameon=False,
                                xlim=(-0.05, width + 0.05),
                                ylim=(-0.05, height + 0.05))
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_formatter(plt.NullFormatter())
        axis.set_major_locator(plt.NullLocator())

    # Draw a grid in the background
    for r in range(height):
        for c in range(width):
            edge_color = '#888888'
            if grid_colors is not None:
                face_color = grid_colors[r, c]
            else:
                face_color = 'white'
            
            drawing = RegularPolygon((c + 0.5, (height - 1 - r) + 0.5),
                                         numVertices=4,
                                         radius=0.5 * np.sqrt(2),
                                         orientation=np.pi / 4,
                                         ec=edge_color,
                                         fc=face_color)
            ax.add_patch(drawing)

    return fig, ax

def render_from_layout(layout, get_token_images, dpi=150, grid_colors=None):
    height, width = layout.shape[:2]

    fig, ax = initialize_figure(height, width, grid_colors=grid_colors)

    for r in range(height):
        for c in range(width):
            token_images = get_token_images(layout[r, c])
            for im in token_images:
                draw_token(im, r, c, ax, height, width)

    im = fig2data(fig, dpi=dpi)
    plt.close(fig)

    im = Image.fromarray(im)
    new_width, new_height = (int(im.size[0] * IM_SCALE), int(im.size[1] * IM_SCALE))
    # TODO : switch resize method to Image.Resampling.LANCZOS when pillow>=10 is supported
    im = im.resize((new_width, new_height), Image.ANTIALIAS)
    im = np.array(im)

    return im

def draw_token(token_image, r, c, ax, height, width, token_scale=1.0, fig_scale=1.0):
    oi = OffsetImage(token_image, zoom = fig_scale * (token_scale / max(height, width)**0.5))
    box = AnnotationBbox(oi, (c + 0.5, (height - 1 - r) + 0.5), frameon=False)
    ax.add_artist(box)
    return box


################################################################
# no margins

from skimage.transform import resize

def render_from_layout_crisp(layout, get_token_images, tilesize=16):
    height, width = layout.shape[:2]
    canvas = np.zeros((height*tilesize,width*tilesize,3))

    for r in range(height):
        for c in range(width):
            token_images = get_token_images(layout[r, c])
            for im in token_images:
                canvas[r*tilesize:(r+1)*tilesize, c*tilesize:(c+1)*tilesize] = \
                    resize(im[:,:,:3], (tilesize,tilesize,3), preserve_range=True)

    return canvas
