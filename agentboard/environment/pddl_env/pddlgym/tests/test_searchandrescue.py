import pddlgym
import numpy as np

import unittest


class TestSearchAndRescue(unittest.TestCase):
    def skip_test_searchandrescue(self, num_actions_to_test=10, verbose=False):
        """Test state encoding and decoding
        """
        for level in range(1, 7):
            env = pddlgym.make(f"SearchAndRescueLevel{level}-v0")
            if level == 1:
                assert len(env.problems) == 20
            else:
                assert len(env.problems) == 50
            env.fix_problem_index(0)
            state, debug_info = env.reset()
            rng = np.random.RandomState(0)

            all_actions = env.get_possible_actions()
            actions = rng.choice(all_actions, size=num_actions_to_test)
            done = False
            for t, act in enumerate(actions):
                if verbose:
                    print(f"Taking action {t}/{num_actions_to_test}", end='\r', flush=True)

                assert state == env._internal_to_state(env._state)
                assert env._state.literals == env._state_to_internal(state).literals
                assert env._state.objects == env._state_to_internal(state).objects
                assert set(env._state.goal.literals) == set(env._state_to_internal(state).goal.literals)
                assert env.check_goal(state) == done
                for a in all_actions:
                    ns = env.get_successor_state(state, a)
                    assert ns == env._internal_to_state(env._state_to_internal(ns))

                if done:
                    break
                state, _, done, _ = env.step(act)
            if verbose:
                print()


    def test_searchandrescue_walls(self, num_actions_to_test=10):
        """Test that when we try to move into walls, we stay put.
        """
        rng = np.random.RandomState(0)
        for level in [1, 2]:
            env = pddlgym.make(f"SearchAndRescueLevel{level}-v0")
            for idx in range(len(env.problems)):
                env.fix_problem_index(idx)
                state, debug_info = env.reset()

                all_actions = dropoff, down, left, right, up, pickup = env.get_possible_actions()

                act_to_delta = {
                    dropoff : (0, 0),
                    down : (1, 0),
                    left : (0, -1),
                    right : (0, 1),
                    up : (-1, 0),
                    pickup : (0, 0),
                }

                actions = rng.choice(all_actions, size=num_actions_to_test)
                done = False
                robot_r, robot_c = dict(state)["robot0"]
                walls = { dict(state)[k] for k in dict(state) if k.startswith("wall") } 
                for t, act in enumerate(actions):

                    dr, dc = act_to_delta[act]
                    can_r, can_c = robot_r + dr, robot_c + dc

                    if done:
                        break
                    state1, _, done, _ = env.step(act)
                    state2 = env.get_successor_state(state, act)
                    assert state2 == state1
                    state = state1

                    new_r, new_c = dict(state)["robot0"]

                    if (can_r, can_c) in walls:
                        # Can't move into walls!
                        assert (new_r, new_c) == (robot_r, robot_c)

                    robot_r, robot_c = new_r, new_c


if __name__ == "__main__":
    # test_searchandrescue(verbose=True)
    # test_searchandrescue_walls()
    unittest.main()
