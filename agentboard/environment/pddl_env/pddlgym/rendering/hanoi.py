from .utils import fig2data

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches


def get_objects_from_obs(obs):
    all_objs = set()
    discs = set()
    disc_pair_order = set()

    # A peg is a largest object
    for lit in obs:
        if lit.predicate.name == 'smaller':
            larger, smaller = lit.variables
            all_objs.update({larger, smaller})
            discs.add(smaller)
            disc_pair_order.add((larger, smaller))

    pegs = sorted(all_objs - discs)

    # Get discs ordered by size
    discs_ordered_by_size = []
    while len(discs):
        for d1 in discs:
            is_next = True
            for d2 in discs:
                if d1 == d2:
                    continue
                if (d2, d1) in disc_pair_order:
                    is_next = False
                    break
            if is_next:
                break
        else:
            import ipdb; ipdb.set_trace()
        discs_ordered_by_size.append(d1)
        discs.remove(d1)

    # Get peg_to_disc_list
    on_links = {}
    for lit in obs:
        if lit.predicate.name == 'on':
            on_links[lit.variables[1]] = lit.variables[0]

    peg_to_disc_list = {}
    for peg in pegs:
        disc_list = []
        key = peg
        while key in on_links:
            disc_list.append(on_links[key])
            key = on_links[key]
        peg_to_disc_list[peg] = disc_list

    return pegs, discs_ordered_by_size, peg_to_disc_list

def get_peg_params(pegs, width, height):
    peg_width = (width / 10.) / len(pegs)
    vertical_padding = height * 0.2
    peg_height = height - vertical_padding
    boundaries = np.linspace(0, width, len(pegs)+1)
    interval = (boundaries[1] - boundaries[0]) / 2
    peg_midpoints = boundaries[:-1] + interval
    peg_to_hor_midpoints = dict(zip(pegs, peg_midpoints))
    return peg_width, peg_height, peg_to_hor_midpoints

def get_disc_params(discs_ordered_by_size, peg_to_disc_list, peg_to_hor_midpoints, width, peg_height):
    num_pegs = len(peg_to_hor_midpoints)
    num_discs = len(discs_ordered_by_size)
    disc_height = (peg_height * 0.75) / num_discs

    horizontal_padding = width * 0.1
    max_disc_width = width / num_pegs - horizontal_padding
    min_disc_width = max_disc_width / 3
    all_disc_widths = np.linspace(max_disc_width, min_disc_width, num_discs)
    disc_widths = dict(zip(discs_ordered_by_size, all_disc_widths))

    disc_midpoints = {}
    for peg, discs in peg_to_disc_list.items():
        x = peg_to_hor_midpoints[peg]
        for i, disc in enumerate(discs):
            y = i * disc_height + disc_height / 2
            disc_midpoints[disc] = (x, y)

    return disc_height, disc_midpoints, disc_widths

def draw_pegs(ax, peg_width, peg_height, peg_to_hor_midpoints, height):
    for midx in peg_to_hor_midpoints.values():
        x = midx - peg_width / 2
        y = 0
        rect = patches.Rectangle((x,y), peg_width, peg_height, 
            linewidth=1, edgecolor=(0.2,0.2,0.2), facecolor=(0.5,0.5,0.5))
        ax.add_patch(rect)

def draw_discs(ax, disc_height, disc_midpoints, disc_widths):
    for disc, (midx, midy) in disc_midpoints.items():
        disc_width = disc_widths[disc]
        x = midx - disc_width / 2
        y = midy - disc_height / 2
        rect = patches.Rectangle((x,y), disc_width, disc_height, 
            linewidth=1, edgecolor=(0.2,0.2,0.2), facecolor=(0.8,0.1,0.1))
        ax.add_patch(rect)

def render(obs, mode='human', close=False):

    width, height = 4.2, 1.5
    fig = plt.figure(figsize=(width, height))
    ax = fig.add_axes((0.0, 0.0, 1.0, 1.0),
                                aspect='equal', frameon=False,
                                xlim=(-0.05, width + 0.05),
                                ylim=(-0.05, height + 0.05))
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_formatter(plt.NullFormatter())
        axis.set_major_locator(plt.NullLocator())

    pegs, discs_ordered_by_size, peg_to_disc_list = get_objects_from_obs(obs)
    peg_width, peg_height, peg_to_hor_midpoints = get_peg_params(pegs, width, height)
    disc_height, disc_midpoints, disc_widths = get_disc_params(discs_ordered_by_size, 
        peg_to_disc_list, peg_to_hor_midpoints, width, peg_height)

    draw_pegs(ax, peg_width, peg_height, peg_to_hor_midpoints, height)
    draw_discs(ax, disc_height, disc_midpoints, disc_widths)

    return fig2data(fig)
