from pddlgym.parser import PDDLDomainParser, PDDLProblemParser
from pddlgym.structs import LiteralConjunction
from pddlgym.planning import run_ff, PlanningException
import pddlgym
import os
import numpy as np
from itertools import count
np.random.seed(0)


PDDLDIR = os.path.join(os.path.dirname(pddlgym.__file__), "pddl")
DOMAIN_NAME = "searchandrescue"


def get_random_location(locations_in_grid, disallowed_mask=None, rng=np.random):
    while True:
        r = rng.randint(locations_in_grid.shape[0])
        c = rng.randint(locations_in_grid.shape[1])
        if disallowed_mask is None or not disallowed_mask[r, c]:
            return locations_in_grid[r, c]

def sample_state(domain, num_rows=6, num_cols=6,
                 num_people=1,
                 randomize_person_loc=False,
                 randomize_robot_start=True,
                 wall_probability=0.2,
                 randomize_walls=False,
                 randomize_hospital_loc=False,
                 num_chickens=0):

    person_type = domain.types['person']
    robot_type = domain.types['robot']
    location_type = domain.types['location']
    wall_type = domain.types['wall']
    hospital_type = domain.types['hospital']
    chicken_type = domain.types['chicken']
    conn = domain.predicates['conn']
    clear = domain.predicates['clear']
    robot_at = domain.predicates['robot-at']
    person_at = domain.predicates['person-at']
    wall_at = domain.predicates['wall-at']
    hospital_at = domain.predicates['hospital-at']
    chicken_at = domain.predicates['chicken-at']
    handsfree = domain.predicates['handsfree']
    move = domain.predicates['move']
    pickup = domain.predicates['pickup']
    dropoff = domain.predicates['dropoff']

    objects = set()
    state = set()
    locations_in_grid = np.empty((num_rows,  num_cols), dtype=object)
    occupied_locations = set()

    # Generate locations
    for r in range(num_rows):
        for c in range(num_cols):
            loc = location_type(f"f{r}-{c}f")
            locations_in_grid[r, c] = loc
            objects.add(loc)

    # Add connections
    for r in range(num_rows):
        for c in range(num_cols):
            loc = locations_in_grid[r, c]
            if r > 0:
                state.add(conn(loc, locations_in_grid[r-1, c], 'up'))
            if r < num_rows - 1:
                state.add(conn(loc, locations_in_grid[r+1, c], 'down'))
            if c > 0:
                state.add(conn(loc, locations_in_grid[r, c-1], 'left'))
            if c < num_cols - 1:
                state.add(conn(loc, locations_in_grid[r, c+1], 'right'))

    # Generate walls
    if randomize_walls:
        wall_rng = np.random
    else:
        wall_rng =  np.random.RandomState(0)
    wall_mask = wall_rng.uniform(size=(num_rows, num_cols)) < wall_probability
    # Hack
    wall_mask[0, 0] = 0
    wall_mask[-1, -1] = 0

    # Add robot
    robot = robot_type("robot0")
    objects.add(robot)
    state.add(handsfree(robot))
    
    # Get robot location
    if randomize_robot_start:
        robot_loc = get_random_location(locations_in_grid,
            disallowed_mask=wall_mask)
    else:
        robot_loc = locations_in_grid[0, 0]
    occupied_locations.add(robot_loc)
    state.add(robot_at(robot, robot_loc))

    # Add hospital
    hospital = hospital_type("hospital0")
    objects.add(hospital)

    # Get hospital loc
    if randomize_hospital_loc:
        hospital_loc = get_random_location(locations_in_grid,
            disallowed_mask=wall_mask)
    else:
        hospital_loc = locations_in_grid[-1, -1]
    occupied_locations.add(hospital_loc)
    state.add(hospital_at(hospital, hospital_loc))

    # Add people
    people = []
    for person_idx in range(num_people):
        person = person_type(f"person{person_idx}")
        objects.add(person)
        people.append(person)

    # Get people locations
    for person_idx, person in enumerate(people):
        if randomize_person_loc:
            loc = get_random_location(locations_in_grid,
                disallowed_mask=wall_mask)
        else:
            loc = get_random_location(locations_in_grid,
                disallowed_mask=wall_mask,
                rng=np.random.RandomState(123+person_idx))
        occupied_locations.add(loc)
        state.add(person_at(person, loc))

    # Add chickens
    chickens = []
    for chicken_idx in range(num_chickens):
        chicken = chicken_type(f"chicken{chicken_idx}")
        objects.add(chicken)
        chickens.append(chicken)

    # Get people locations
    for chicken_idx, chicken in enumerate(chickens):
        loc = get_random_location(locations_in_grid,
            disallowed_mask=wall_mask)
        occupied_locations.add(loc)
        state.add(chicken_at(chicken, loc))

    for r in range(num_rows):
        for c in range(num_cols):
            loc = locations_in_grid[r, c]
            # Don't allow walls at occupied locs
            if loc not in occupied_locations and wall_mask[r, c]:
                wall = wall_type(f"wall{r}-{c}")
                objects.add(wall)
                state.add(wall_at(wall, loc))
            elif loc != robot_loc:
                state.add(clear(loc))

    # Generate actions
    for person in people:
        state.add(pickup(person))
    state.add(dropoff())
    for direction in domain.constants:
        state.add(move(direction))

    return objects, state, people, hospital_loc

def create_goal(domain, people, hospital_loc, num_selected_people=1):
    person_at = domain.predicates['person-at']
    goal_lits = []
    selected_people = np.random.choice(people, size=num_selected_people, replace=False)
    for person in selected_people:
        goal_lits.append(person_at(person, hospital_loc))
    return LiteralConjunction(goal_lits)

def sample_problem(domain, problem_dir, problem_outfile, 
                   num_rows=6, num_cols=6,
                   num_people=1, num_selected_people=1,
                   randomize_person_loc=False,
                   randomize_robot_start=True,
                   wall_probability=0.2,
                   randomize_walls=False,
                   randomize_hospital_loc=False,
                   num_chickens=0):
    
    all_objects, initial_state, people, hospital_loc = sample_state(domain, 
        num_rows=num_rows, num_cols=num_cols,
        num_people=num_people,
        randomize_person_loc=randomize_person_loc,
        randomize_robot_start=randomize_robot_start,
        wall_probability=wall_probability,
        randomize_walls=randomize_walls,
        randomize_hospital_loc=randomize_hospital_loc,
        num_chickens=num_chickens,
    )

    if isinstance(num_selected_people, tuple):
        lo, hi = num_selected_people
        num_selected_people = np.random.randint(lo, hi+1)

    goal = create_goal(domain, people, hospital_loc, 
        num_selected_people=num_selected_people)

    filedir = os.path.join(PDDLDIR, problem_dir)
    os.makedirs(filedir, exist_ok=True)
    filepath = os.path.join(filedir, problem_outfile)

    PDDLProblemParser.create_pddl_file(
        filepath,
        objects=all_objects,
        initial_state=initial_state,
        problem_name=DOMAIN_NAME,
        domain_name=domain.domain_name,
        goal=goal,
        fast_downward_order=True,
    )
    print("Wrote out to {}.".format(filepath))
    problem_id = (frozenset(initial_state), goal)
    return problem_id, filepath

def problem_is_valid(domain, problem_filepath):
    # Verify that plan can be found
    try:
        plan = run_ff(domain.domain_fname, problem_filepath)
    except PlanningException:
        return False
    # Make sure plan is nontrivial
    return len(plan) > 0

def generate_problems(num_train=50, num_test=10, level=1, **kwargs):
    domain = PDDLDomainParser(os.path.join(PDDLDIR, f"{DOMAIN_NAME}.pddl"),
        expect_action_preds=True,
        operators_as_actions=False)

    # Create version of the domain for simplicity
    domain_name_with_level = f"{DOMAIN_NAME}_level{level}"
    domain.write(os.path.join(PDDLDIR, f"{domain_name_with_level}.pddl"))

    # Make sure problems are unique
    seen_problem_ids = set()

    problem_idx = 0
    while problem_idx < num_train + num_test:
        if problem_idx < num_train:
            problem_dir = domain_name_with_level
        else:
            problem_dir = f"{domain_name_with_level}_test"
        problem_outfile = f"problem{problem_idx}.pddl"
        problem_id, problem_filepath = sample_problem(domain, problem_dir, 
            problem_outfile, **kwargs)
        if problem_id in seen_problem_ids:
            continue
        seen_problem_ids.add(problem_id)
        if problem_is_valid(domain, problem_filepath):
            problem_idx += 1


if __name__ == "__main__":
    generate_problems(
        num_train=20,
        level=1,
        num_people=1, 
        num_selected_people=1,
        randomize_person_loc=False,
        randomize_robot_start=True,
        randomize_walls=False,
        randomize_hospital_loc=False)

    generate_problems(level=2,
        num_people=1, 
        num_selected_people=1,
        randomize_person_loc=True, # !
        randomize_robot_start=True,
        randomize_walls=False,
        randomize_hospital_loc=False)

    generate_problems(level=3,
        num_people=1, 
        num_selected_people=1,
        randomize_person_loc=True,
        randomize_robot_start=True,
        randomize_walls=False,
        randomize_hospital_loc=True, # !
    )

    generate_problems(level=4,
        num_people=3, # !
        num_selected_people=1,
        randomize_person_loc=True,
        randomize_robot_start=True,
        randomize_walls=False,
        randomize_hospital_loc=True,
    )

    generate_problems(level=5,
        num_people=3,
        num_selected_people=(2, 3), # !
        randomize_person_loc=True,
        randomize_robot_start=True,
        randomize_walls=False,
        randomize_hospital_loc=True,
    )

    generate_problems(level=6,
        num_people=3,
        num_selected_people=(2, 3),
        randomize_person_loc=True,
        randomize_robot_start=True,
        randomize_walls=True, # !
        randomize_hospital_loc=True,
    )

    # generate_problems(level=7,
    #     num_people=1,
    #     num_selected_people=1,
    #     randomize_person_loc=False,
    #     randomize_robot_start=True,
    #     randomize_walls=False,
    #     randomize_hospital_loc=False,
    #     num_chickens=5, # !
    # )
