from pddlgym.parser import PDDLDomainParser, PDDLProblemParser
from pddlgym.structs import LiteralConjunction
import pddlgym
import os
import numpy as np
from itertools import count
np.random.seed(0)


PDDLDIR = os.path.join(os.path.dirname(pddlgym.__file__), "pddl")

def sample_state(domain, num_balls, num_rooms):
    room = domain.predicates['room']
    ball = domain.predicates['ball']
    gripper = domain.predicates['gripper']
    at_robby = domain.predicates['at-robby']
    at = domain.predicates['at']
    free = domain.predicates['free']

    objects = set()
    state = set()

    # Generate rooms
    room_idx = count()
    rooms = []
    for _ in range(num_rooms):
        room_obj = "room{}".format(next(room_idx))
        rooms.append(room_obj)
        objects.add(room_obj)
        state.add(room(room_obj))

    # Generate grippers and robby
    for gripper_idx in range(2):
        gripper_obj = "gripper{}".format(gripper_idx)
        objects.add(gripper_obj)
        state.add(gripper(gripper_obj))
        state.add(free(gripper_obj))
    state.add(at_robby("room0"))

    # Generate balls
    ball_idx = count()
    balls = []
    for _ in range(num_balls):
        ball_obj = "ball{}".format(next(ball_idx))
        balls.append(ball_obj)
        objects.add(ball_obj)
        state.add(ball(ball_obj))
        room_for_ball = rooms[np.random.choice(len(rooms))]
        state.add(at(ball_obj, room_for_ball))

    return objects, balls, rooms, state

def create_goal(domain, balls, rooms, num_balls):
    at = domain.predicates['at']

    goal_balls = [balls[i] for i in np.random.choice(len(balls), replace=False, size=num_balls)]
    goal_lits = []

    for ball in goal_balls:
        room = rooms[np.random.choice(len(rooms))]
        goal_lits.append(at(ball, room))

    return LiteralConjunction(goal_lits)

def sample_problem(domain, problem_dir, problem_outfile, 
                   min_num_balls=201, max_num_balls=300,
                   min_num_rooms=101, max_num_rooms=200,
                   min_num_balls_goal=5, max_num_balls_goal=20):
    
    all_objects, balls, rooms, initial_state = sample_state(domain, 
        num_balls=np.random.randint(min_num_balls, max_num_balls+1),
        num_rooms=np.random.randint(min_num_rooms, max_num_rooms+1),
    )
    goal = create_goal(domain, balls, rooms, 
        num_balls=np.random.randint(min_num_balls_goal, max_num_balls_goal+1))

    filepath = os.path.join(PDDLDIR, problem_dir, problem_outfile)

    PDDLProblemParser.create_pddl_file(
        filepath,
        objects=all_objects,
        initial_state=initial_state,
        problem_name="manygripper",
        domain_name=domain.domain_name,
        goal=goal,
        fast_downward_order=True,
    )
    print("Wrote out to {}.".format(filepath))

def generate_problems():
    domain = PDDLDomainParser(os.path.join(PDDLDIR, "manygripper.pddl"),
        expect_action_preds=False,
        operators_as_actions=True)

    for problem_idx in range(40): #50):

        if problem_idx < 40:
            problem_dir = "manygripper"
        else:
            problem_dir = "manygripper_test"
        problem_outfile = "problem{}.pddl".format(problem_idx)

        if problem_idx < 40:
            sample_problem(domain, problem_dir, problem_outfile, 
               min_num_balls=20, max_num_balls=30,
               min_num_rooms=10, max_num_rooms=20,
               min_num_balls_goal=2, max_num_balls_goal=5,
            )
        else:
            sample_problem(domain, problem_dir, problem_outfile, 
               min_num_balls=201, max_num_balls=300,
               min_num_rooms=101, max_num_rooms=200,
               min_num_balls_goal=5, max_num_balls_goal=20,
            )

if __name__ == "__main__":
    generate_problems()
