"""Utilities
"""
from collections import defaultdict
import contextlib
import sys
import itertools
import numpy as np
import os
import gym
import imageio


def get_object_combinations(objects, arity, var_types=None, 
                            type_to_parent_types=None, allow_duplicates=False):
    type_to_objs = defaultdict(list)

    for obj in sorted(objects):
        if type_to_parent_types is None:
            type_to_objs[obj.var_type].append(obj)
        else:
            for t in type_to_parent_types[obj.var_type]:
                type_to_objs[t].append(obj)

    if var_types is None:
        choices = [sorted(objects) for _ in range(arity)]
    else:
        assert len(var_types) == arity
        choices = [type_to_objs[vt] for vt in var_types]

    for choice in itertools.product(*choices):
        if not allow_duplicates and len(set(choice)) != len(choice):
            continue
        yield choice

def run_demo(env, policy, max_num_steps=10, render=False,
             video_path=None, fps=3, verbose=False, seed=None,
             check_reward=False):

    images = []

    if seed is not None:
        env.seed(seed)

    obs, _ = env.reset()

    if seed is not None:
        env.action_space.seed(seed)

    for t in range(max_num_steps):
        if verbose:
            print("Obs:", obs)

        if render:
            images.append(env.render())
    
        action = policy(obs)
        if verbose:
            print("Act:", action)

        obs, reward, done, _ = env.step(action)
        env.render()
        if verbose:
            print("Rew:", reward)

        if done:
            break

    if verbose:
        print("Final obs:", obs)
        print()

    if render:
        images.append(env.render())
        imageio.mimwrite(video_path, images, fps=fps)
        print("Wrote out video to", video_path)

    env.close()
    if check_reward:
        assert tot_reward > 0
    if verbose:
        input("press enter to continue to next problem")


class DummyFile:
    def write(self, x):
        pass

    def flush(self):
        pass


@contextlib.contextmanager
def nostdout():
    save_stdout = sys.stdout
    sys.stdout = DummyFile()
    yield
    sys.stdout = save_stdout
