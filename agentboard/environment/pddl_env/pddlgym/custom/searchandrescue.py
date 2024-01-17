from pddlgym.core import PDDLEnv
from pddlgym.rendering import sar_render, slow_sar_render, posar_render, myopic_posar_render
from pddlgym.structs import Type, Predicate, Not, State, LiteralConjunction
import gym
import functools
import pddlgym
import os
import numpy as np


def get_sar_successor_state(state, action):
    """Search and rescue specific successor generation

    Assumptions:
        - One robot called robot0
    """
    # Remake predicates to keep this function self-contained
    person_type = Type('person')
    robot_type = Type('robot')
    location_type = Type('location')
    direction_type = Type('direction')
    clear = Predicate('clear', 1, [location_type])
    conn = Predicate("conn", 3, [location_type, location_type, direction_type])
    robot_at = Predicate('robot-at', 2, [robot_type, location_type])
    carrying = Predicate('carrying', 2, [robot_type, person_type])
    person_at = Predicate('person-at', 2, [person_type, location_type])
    handsfree = Predicate('handsfree', 1, [robot_type])

    # Parse the state
    robot_location = None # location
    robot_carrying = None # person
    adjacency_map = {} # (location, direction) -> location
    people_locs = {} # person -> location
    clear_locs = set()

    for lit in state.literals:
        if lit.predicate.name == "robot-at":
            assert lit.variables[0] == "robot0"
            robot_location = lit.variables[1]
        elif lit.predicate.name == "conn":
            adjacency_map[(lit.variables[0], lit.variables[2])] = lit.variables[1]
        elif lit.predicate.name == "carrying":
            assert lit.variables[0] == "robot0"
            robot_carrying = lit.variables[1]
        elif lit.predicate.name == "person-at":
            people_locs[lit.variables[0]] = lit.variables[1]
        elif lit.predicate.name == "clear":
            clear_locs.add(lit.variables[0])

    assert robot_location is not None

    is_valid = False
    pos_preconds = set()
    neg_preconds = set()
    pos_effects = set()
    neg_effects = set()

    if action.predicate.name == "move":
        """
        (:action move-robot
        :parameters (?robot - robot ?from - location ?to - location ?dir - direction)
        :precondition (and (move ?dir)
            (conn ?from ?to ?dir)
            (robot-at ?robot ?from)
            (clear ?to))
        :effect (and
            (not (robot-at ?robot ?from))
            (robot-at ?robot ?to)
            (not (clear ?to))
            (clear ?from))
        )
        """
        direction = action.variables[0]
        if (robot_location, direction) in adjacency_map:
            next_robot_location = adjacency_map[(robot_location, direction)]
            if next_robot_location in clear_locs:
                is_valid = True
                pos_preconds = { 
                    conn(robot_location, next_robot_location, direction),
                    robot_at("robot0", robot_location),
                    clear(next_robot_location),
                }
                pos_effects = {
                    robot_at("robot0", next_robot_location),
                    clear(robot_location)
                }
                neg_effects = {
                    robot_at("robot0", robot_location),
                    clear(next_robot_location)
                }

    elif action.predicate.name == "pickup":
        """
        (:action pickup-person
            :parameters (?robot - robot ?person - person ?loc - location)
            :precondition (and (pickup ?person)
                (robot-at ?robot ?loc)
                (person-at ?person ?loc)
                (handsfree ?robot))
            :effect (and
                (not (person-at ?person ?loc))
                (not (handsfree ?robot))
                (carrying ?robot ?person))
        )
        """
        if robot_carrying is None:
            person = action.variables[0]
            person_loc = people_locs[person]
            if person_loc == robot_location:
                is_valid = True
                pos_preconds = { 
                    robot_at("robot0", robot_location),
                    person_at(person, person_loc),
                    handsfree("robot0"),
                }
                pos_effects = {
                    carrying("robot0", person),
                }
                neg_effects = {
                    person_at(person, person_loc),
                    handsfree("robot0"),
                }

    elif action.predicate.name == "dropoff":
        """
        (:action dropoff-person
        :parameters (?robot - robot ?person - person ?loc - location)
        :precondition (and (dropoff )
            (carrying ?robot ?person)
            (robot-at ?robot ?loc))
        :effect (and
            (person-at ?person ?loc)
            (handsfree ?robot)
            (not (carrying ?robot ?person)))
        )
        """
        if robot_carrying is not None:
            is_valid = True
            pos_preconds = { 
                robot_at("robot0", robot_location),
                carrying("robot0", robot_carrying),
            }
            pos_effects = {
                person_at(robot_carrying, robot_location),
                handsfree("robot0"),
            }
            neg_effects = {
                carrying("robot0", robot_carrying),
            }

    else:
        raise Exception(f"Unrecognized action {action}.")

    if not is_valid:
        return state

    assert state.literals.issuperset(pos_preconds)
    assert len(state.literals & {Not(p) for p in neg_preconds}) == 0
    new_state_literals = set(state.literals)
    new_state_literals -= neg_effects
    new_state_literals |= pos_effects
    return state.with_literals(frozenset(new_state_literals))


class PDDLSearchAndRescueEnv(PDDLEnv):

    def __init__(self, level=1, test=False, render_version="fast"):
        dir_path = os.path.join(os.path.dirname(os.path.realpath(pddlgym.__file__)), "pddl")
        domain_file = os.path.join(dir_path, "searchandrescue.pddl")
        problem_dir = os.path.join(dir_path, f"searchandrescue_level{level}")
        if test:
            problem_dir += "_test"
        if render_version == "fast":
            render = sar_render
        else:
            assert render_version == "slow"
            render = slow_sar_render
        super().__init__(domain_file=domain_file, problem_dir=problem_dir, render=render)

    def _get_successor_state(self, state, action, domain, **kwargs):
        """Custom (faster than generic)
        """
        return get_sar_successor_state(state, action)

    def get_successor_state(self, state, action):
        """Allow for public access
        """
        return self._get_successor_state(state, action, self.domain)

    def get_possible_actions(self):
        """Light wrapper around the action space, for convenience.
        """
        assert not self._dynamic_action_space
        if not self._state:
            raise Exception("Must all reset() before get_possible_actions().")
        return sorted(self.action_space.all_ground_literals(self._state))

    def _action_valid_test(self, state, action):
        """
        """
        raise NotImplementedError("Should not be called.")

    def render_from_state(self, state):
        """Light wrapper around the render function, for convenience
        """
        return self._render(state.literals)

    def check_goal(self, state):
        """Allow for public access
        """
        return self._is_goal_reached(state)


class SearchAndRescueEnv(PDDLSearchAndRescueEnv):
    """Changes the state space to just be positions of objects
    and the identity of the person being carried.
    """
    person_type = Type('person')
    robot_type = Type('robot')
    location_type = Type('location')
    direction_type = Type('direction')
    wall_type = Type('wall')
    hospital_type = Type('hospital')
    clear = Predicate('clear', 1, [location_type])
    conn = Predicate("conn", 3, [location_type, location_type, direction_type])
    robot_at = Predicate('robot-at', 2, [robot_type, location_type])
    person_at = Predicate('person-at', 2, [person_type, location_type])
    wall_at = Predicate('wall-at', 2, [wall_type, location_type])
    hospital_at = Predicate('hospital-at', 2, [hospital_type, location_type])
    carrying = Predicate('carrying', 2, [robot_type, person_type])
    handsfree = Predicate('handsfree', 1, [robot_type])

    @property
    def observation_space(self):
        raise NotImplementedError()

    def _state_to_internal(self, state):
        state = dict(state)
        new_state_literals = set()

        directions_to_deltas = {
            self.direction_type('up') : (-1, 0),
            self.direction_type('down') : (1, 0),
            self.direction_type('left') : (0, -1),
            self.direction_type('right') : (0, 1),
        }

        # conn
        height, width = 6, 6
        for r in range(height):
            for c in range(width):
                loc = self.location_type(f"f{r}-{c}f")
                for direction, (dr, dc) in directions_to_deltas.items():
                    next_r, next_c = r + dr, c + dc
                    if not (0 <= next_r < height and 0 <= next_c < width):
                        continue
                    next_loc = self.location_type(f"f{next_r}-{next_c}f")
                    conn_lit = self.conn(loc, next_loc, direction)
                    new_state_literals.add(conn_lit)

        # at
        occupied_locs = set()
        hospital_loc = None
        for obj_name, loc_tup in state.items():
            if obj_name in ["carrying", "rescue"]:
                continue
            r, c = loc_tup
            loc = self.location_type(f"f{r}-{c}f")
            if obj_name.startswith("person"):
                at_pred = self.person_at
            elif obj_name.startswith("robot"):
                at_pred = self.robot_at
                occupied_locs.add((r, c))
            elif obj_name.startswith("wall"):
                at_pred = self.wall_at
                occupied_locs.add((r, c))
            elif obj_name.startswith("hospital"):
                at_pred = self.hospital_at
                assert hospital_loc is None
                hospital_loc = loc
            else:
                raise Exception(f"Unrecognized object {obj_name}")
            new_state_literals.add(at_pred(obj_name, loc))
        assert hospital_loc is not None

        # carrying/handsfree
        if state["carrying"] is None:
            new_state_literals.add(self.handsfree("robot0"))
        else:
            new_state_literals.add(self.carrying("robot0", state["carrying"]))

        # clear
        for r in range(height):
            for c in range(width):
                if (r, c) not in occupied_locs:
                    loc = self.location_type(f"f{r}-{c}f")
                    clear_lit = self.clear(loc)
                    new_state_literals.add(clear_lit)

        # objects
        new_objects = frozenset({o for lit in new_state_literals for o in lit.variables })

        # goal
        new_goal = LiteralConjunction([self.person_at(person, hospital_loc) \
            for person in sorted(state["rescue"])])

        new_state = State(frozenset(new_state_literals), new_objects, new_goal)

        return new_state

    def _internal_to_state(self, internal_state):
        state = { "carrying" : None }
        state["rescue"] = set()
        for lit in internal_state.goal.literals:
            assert lit.predicate == self.person_at
            state["rescue"].add(lit.variables[0].name)
        state["rescue"] = frozenset(state["rescue"]) # make hashable
        for lit in internal_state.literals:
            if lit.predicate.name.endswith("at"):
                obj_name = lit.variables[0].name
                r, c = self._loc_to_rc(lit.variables[1])
                state[obj_name] = (r, c)
            if lit.predicate.name == "carrying":
                person_name = lit.variables[1].name
                state["carrying"] = person_name
        state = tuple(sorted(state.items())) # make hashable
        return state

    def _loc_to_rc(self, loc_str):
        assert loc_str.startswith("f") and loc_str.endswith("f")
        r, c = loc_str[1:-1].split('-')
        return (int(r), int(c))

    def set_state(self, state):
        assert isinstance(state, State), "Do not call set_state"
        self._state = state

    def get_state(self):
        assert isinstance(self._state, State), "Do not call get_state"
        return self._state

    def reset(self):
        internal_state, debug_info = super().reset()
        return self._internal_to_state(internal_state), debug_info

    def step(self, action):
        internal_state, reward, done, debug_info = super().step(action)
        state = self._internal_to_state(internal_state)
        return state, reward, done, debug_info

    def get_successor_state(self, state, action):
        internal_state = self._state_to_internal(state)
        next_internal_state = super().get_successor_state(internal_state, action)
        next_state = self._internal_to_state(next_internal_state)
        # Sanity checks
        assert state == self._internal_to_state(internal_state)
        assert next_internal_state == self._state_to_internal(next_state)
        return next_state

    def render_from_state(self, state):
        internal_state = self._state_to_internal(state)
        return super().render_from_state(internal_state)

    def check_goal(self, state):
        internal_state = self._state_to_internal(state)
        return super().check_goal(internal_state)


class POSARXrayEnv(gym.Env):
    """Partially observable search and rescue
    """
    height, width = 7, 7
    room_locs = [(6, 0), (0, 6), (6, 6), (3, 6)]
    robot_starts = [(4, 3)]
    wall_locs = [(1, 1), (2, 4), (1, 4), (1, 5), (2, 5), (2, 6),
                 (3, 2), (4, 4), (4, 6), (5, 1), (5, 3), (5, 4)]
    fire_locs = [(1, 2), (2, 3), (4, 0)]
    sense_radius = 0
    actions = up, down, left, right, pickup, do_xray = range(6)

    def __init__(self, seed=0):
        self._state = None # set in reset
        self._problem_idx = None
        self.seed(seed)

    @property
    def problems(self):
        return [(s, i) for s in self.robot_starts \
                for i in range(len(self.room_locs))]

    def fix_problem_index(self, idx):
        self._problem_idx = idx

    def seed(self, seed=0):
        self._seed = seed
        self._rng = np.random.RandomState(seed)        

    def reset(self):
        """
        """
        if self._problem_idx is None:
            # Randomize the robot location
            robot_loc = self.robot_starts[self._rng.choice(len(self.robot_starts))]
            # Randomize the location of the person
            person_room_id = self._rng.choice(len(self.room_locs))
        else:
            robot_loc, person_room_id = self.problems[self._problem_idx]
        # Turn xray vision off
        xray = False
        # Set the state
        self._state = self._construct_state(robot=robot_loc, 
            person=person_room_id, xray=xray, rescued=False)
        # Get the observation
        return self.get_observation(self._state), {}

    def _construct_state(self, robot, person, xray, rescued):
        """
        """
        d = {
            "robot" : robot,
            "person" : person,
            "xray" : xray,
            "rescued" : rescued,
        }
        return self._flat_dict_to_hashable(d)

    # @functools.lru_cache(maxsize=10000)
    def get_observation(self, state):
        """
        """
        if state is None:
            state = self._state
        state = dict(state)

        obs = {}

        # We can always see the robot, xray, and rescued state
        obs["robot"] = state["robot"]
        obs["xray"] = state["xray"]
        obs["rescued"] = state["rescued"]

        # Get which rooms are sensed
        sensed_rooms = set()

        # If xray is on, we can see everything
        if state["xray"]:
            sensed_rooms.update(range(len(self.room_locs)))
        # If we are within a radius of a room, we can see into it
        else:
            rob_r, rob_c = state["robot"]
            for room_id, (room_r, room_c) in enumerate(self.room_locs):
                if abs(rob_r - room_r) + abs(rob_c - room_c) <= self.sense_radius:
                    sensed_rooms.add(room_id)

        # Get room observations
        for room_id in range(len(self.room_locs)):
            if room_id not in sensed_rooms:
                obs[f"room{room_id}"] = "?"
            else:
                if (room_id == state["person"]):
                    obs[f"room{room_id}"] = "person"
                else:
                    obs[f"room{room_id}"] = "empty"

        # Make hashable
        return self._flat_dict_to_hashable(obs)

    # @functools.lru_cache(maxsize=10000)
    def observation_to_states(self, obs):
        # Make easier to manipulate
        obs = dict(obs)
        # Create base state
        base_state = {
            "robot" : obs["robot"],
            "rescued" : obs["rescued"],
        }
        if "xray" in obs:
            base_state["xray"] = obs["xray"]
        else:
            base_state["xray"] = False
        # Check whether we're observing a person
        person = None
        for k, v in obs.items():
            if k.startswith("room") and v == "person":
                person = int(k[len("room"):])
        # If the person is observed, there is only one possible state
        if person is not None:
            base_state["person"] = person
            return frozenset([self._flat_dict_to_hashable(base_state)])
        # Otherwise, the person could be in any room that is hidden
        states = []
        for k, v in obs.items():
            if k.startswith("room") and v == "?":
                person = int(k[len("room"):])
                state = base_state.copy()
                state["person"] = person
                states.append(self._flat_dict_to_hashable(state))
        return frozenset(states)

    def get_possible_actions(self):
        return list(self.actions)

    # @functools.lru_cache(maxsize=10000)
    def get_successor_state(self, state, action):
        state = dict(state)
        assert action in self.actions, f"Invalid action {action}"

        # Start out with previous values
        robot, person, xray = state["robot"], state["person"], state["xray"]

        # Turn on xray
        if action == self.do_xray:
            xray = True

        # Move
        elif action in [self.up, self.down, self.left, self.right]:
            # If we're in a fire location, we're trapped forever
            if robot not in self.fire_locs:
                rob_r, rob_c = robot
                dr, dc = {self.up : (-1, 0), self.down : (1, 0),
                          self.right : (0, 1), self.left : (0, -1)}[action]

                if 0 <= rob_r + dr < self.height and 0 <= rob_c + dc < self.width:
                    if (rob_r + dr, rob_c + dc) not in self.wall_locs:
                        robot = (rob_r + dr, rob_c + dc)

        # Pickup
        if state['rescued'] or \
            (action == self.pickup and robot == self.room_locs[person]):
            rescued = True
        else:
            rescued = False

        # Update the previous state
        return self._construct_state(robot, person, xray, rescued)

    def check_goal(self, state):
        state = dict(state)
        return state["rescued"]

    def step(self, action):
        """
        """
        self._state = self.get_successor_state(self._state, action)

        # We're done if the person is rescued
        done = self.check_goal(self._state)
        reward = float(done)

        return self.get_observation(self._state), reward, done, {}

    def render(self, *args, **kwargs):
        return posar_render(self.get_observation(self._state), self)

    def render_from_state(self, state):
        return posar_render(self.get_observation(state=state), self)

    def _flat_dict_to_hashable(self, d):
        return tuple(sorted(d.items()))


class POSARNoXrayEnv(POSARXrayEnv):
    actions = up, down, left, right, pickup = range(5)

    def get_observation(self, *args, **kwargs):
        obs = super().get_observation(*args, **kwargs)
        obs = dict(obs)
        assert obs["xray"] == False
        del obs["xray"]
        return self._flat_dict_to_hashable(obs)


class MyopicPOSAREnv(gym.Env):
    """The agent now does not know where the fires or people might be
    """
    height, width = 5, 5 # modified in subclasses
    actions = up, down, left, right, pickup = range(5)

    def __init__(self, seed=0):
        self._state = None # set in reset
        self._problem_idx = None
        self.seed(seed)

    @property
    def problems(self):
        raise NotImplementedError("Override me!")

    def fix_problem_index(self, idx):
        self._problem_idx = idx

    def seed(self, seed=0):
        self._seed = seed
        self._rng = np.random.RandomState(seed)        

    def reset(self):
        """
        """
        if self._problem_idx is None:
            problem_idx = self._rng.choice(len(self.problems))
        else:
            problem_idx = self._problem_idx
        # Set state            
        self._state = self.problems[problem_idx]
        # Get the observation
        return self.get_observation(self._state), {}

    def get_possible_actions(self):
        return list(self.actions)

    def get_successor_state(self, state, action):
        state = dict(state)
        assert action in self.actions, f"Invalid action {action}"

        # Start out with previous values
        robot, person = state["robot"], state["person"]

        # Static
        fire_locs = state["fire_locs"]

        # Move
        if action in [self.up, self.down, self.left, self.right]:
            # If we're in a fire location, we're trapped forever
            if robot not in fire_locs:
                rob_r, rob_c = robot
                dr, dc = {self.up : (-1, 0), self.down : (1, 0),
                          self.right : (0, 1), self.left : (0, -1)}[action]

                if 0 <= rob_r + dr < self.height and 0 <= rob_c + dc < self.width:
                    robot = (rob_r + dr, rob_c + dc)

        # Pickup
        if state['rescued'] or (action == self.pickup and robot == person):
            rescued = True
        else:
            rescued = False

        # Update state
        state["robot"] = robot
        state["rescued"] = rescued
        return self._flat_dict_to_hashable(state)

    def check_goal(self, state):
        state = dict(state)
        return state["rescued"]

    def step(self, action):
        """
        """
        self._state = self.get_successor_state(self._state, action)

        # We're done if the person is rescued
        done = self.check_goal(self._state)
        reward = float(done)

        return self.get_observation(self._state), reward, done, {}

    def _flat_dict_to_hashable(self, d):
        return tuple(sorted(d.items()))

    def get_observation(self, state):
        """Can only observe: 
            - the current robot location
            - what's at the location: empty, person, or fire
            - smoke, i.e., a fire that is within manhattan distance 1
            - whether the person has been rescued
        """
        if state is None:
            state = self._state
        state = dict(state)

        obs = {}

        # We can always see the robot and rescued state
        obs["robot"] = state["robot"]
        obs["rescued"] = state["rescued"]

        # We can see what's in the current cell
        rob_r, rob_c = state["robot"]
        cell = "empty"
        # Is the robot at a person?
        if (rob_r, rob_c) == state["person"]:
            cell = "person"
        # Is the robot at a fire?
        elif (rob_r, rob_c) in state["fire_locs"]:
            cell = "fire"
        obs["cell"] = cell

        # Are we fire-adjacent?
        obs["smoke"] = False
        for (dr, dc) in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            if (rob_r + dr, rob_c + dc) in state["fire_locs"]:
                obs["smoke"] = True
                break

        # Make hashable
        return self._flat_dict_to_hashable(obs)

    def observation_to_states(self, obs):
        raise NotImplementedError("There are too many possible states to enumerate!")

    def render(self, *args, **kwargs):
        return myopic_posar_render(self.get_observation(self._state), self)

    def render_from_state(self, state):
        return myopic_posar_render(self.get_observation(state=state), self)


class TinyMyopicPOSAREnv(MyopicPOSAREnv):
    height, width = 1, 5

    @property
    def problems(self):
        initial_states = []

        initial_states.append(self._flat_dict_to_hashable({
            "robot" : (0, 2),
            "person" : (0, 4),
            "fire_locs" : frozenset({(0, 0)}),
            "rescued" : False,
        }))

        initial_states.append(self._flat_dict_to_hashable({
            "robot" : (0, 2),
            "person" : (0, 0),
            "fire_locs" : frozenset({(0, 4)}),
            "rescued" : False,
        }))

        return initial_states



class SmallMyopicPOSAREnv(MyopicPOSAREnv):
    height, width = 3, 5

    @property
    def problems(self):
        initial_states = []

        # Important to not initialize robot in smoke

        initial_states.append(self._flat_dict_to_hashable({
            "robot" : (0, 2),
            "person" : (0, 0),
            "fire_locs" : frozenset({(2, 2)}),
            "rescued" : False,
        }))

        initial_states.append(self._flat_dict_to_hashable({
            "robot" : (1, 2),
            "person" : (2, 0),
            "fire_locs" : frozenset({(0, 1)}),
            "rescued" : False,
        }))

        initial_states.append(self._flat_dict_to_hashable({
            "robot" : (1, 2),
            "person" : (2, 2),
            "fire_locs" : frozenset({(2, 0)}),
            "rescued" : False,
        }))

        initial_states.append(self._flat_dict_to_hashable({
            "robot" : (1, 2),
            "person" : (0, 4),
            "fire_locs" : frozenset({(0, 3), (2, 0)}),
            "rescued" : False,
        }))

        return initial_states


class POSARRadius1Env(POSARNoXrayEnv):
    sense_radius = 1


class POSARRadius1XrayEnv(POSARXrayEnv):
    sense_radius = 1


class POSARRadius0Env(POSARNoXrayEnv):
    sense_radius = 0


class POSARRadius0XrayEnv(POSARXrayEnv):
    sense_radius = 0


class SmallPOSARRadius1Env(POSARRadius1Env):
    height, width = 3, 3
    room_locs = [(0, i) for i in range(3)] + [(2, i) for i in range(3)]
    robot_starts = [(1, 1)]
    wall_locs = []
    fire_locs = []


class SmallPOSARRadius0Env(SmallPOSARRadius1Env):
    sense_radius = 0


class LargePOSARRadius1Env(POSARRadius1Env):
    height, width = 9, 9
    room_locs = [(0, i) for i in range(9)] + [(8, i) for i in range(9)]
    robot_starts = [(4, 3), (4, 4), (4, 5)]
    wall_locs = [(1, 1), (2, 4), (1, 4), (1, 5), (2, 1), (2, 7), (2, 8),
                 (3, 0), (3, 2), (4, 6), (4, 7), (5, 1), (5, 3), (5, 4),
                 (6, 2), (6, 5), (6, 6), (6, 8), (7, 3), (7, 4)]
    fire_locs = []


if __name__ == "__main__":
    import imageio
    np.random.seed(0)
    for env_name in ["PDDLSearchAndRescueLevel7"]: #, "MyopicPOSAR"]:
        imgs = []
        env = pddlgym.make(f"{env_name}-v0")
        env.fix_problem_index(1)
        obs, _ = env.reset()
        print(obs)
        imgs.append(env.render())
        plan = np.random.choice(env.get_possible_actions(), size=50)
        for act in plan:
            obs, reward, done, _ = env.step(act)
            print(obs, reward, done)
            imgs.append(env.render())
            if done:
                break
        imageio.mimsave(f"/tmp/{env_name}_random.mp4", imgs)

