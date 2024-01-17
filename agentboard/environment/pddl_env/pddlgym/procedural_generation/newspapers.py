from pddlgym.parser import PDDLDomainParser, PDDLProblemParser
from pddlgym.structs import LiteralConjunction
import pddlgym
import os
import numpy as np
from itertools import count
np.random.seed(0)


PDDLDIR = os.path.join(os.path.dirname(pddlgym.__file__), "pddl")


def sample_problem(domain, problem_dir, problem_outfile, num_locs,
                   min_extra_papers=1, max_extra_papers=10):
    loc_type = domain.types['loc']
    paper_type = domain.types['paper']
    at = domain.predicates['at']
    isHomeBase = domain.predicates['ishomebase']
    wantsPaper = domain.predicates['wantspaper']
    unpacked = domain.predicates['unpacked']
    satisfied = domain.predicates['satisfied']

    # Create objects and state
    state = set()
    objects = set()
    home_loc = None
    target_locs = []
    # Add locations
    for loc_idx in range(num_locs):
        loc = loc_type(f"loc-{loc_idx}")
        objects.add(loc)
        # home
        if loc_idx == 0:
            state.add(isHomeBase(loc))
            state.add(at(loc))
            home_loc = loc
        # wants paper
        else:
            state.add(wantsPaper(loc))
            target_locs.append(loc)
    # Add papers
    num_papers = num_locs + np.random.randint(min_extra_papers,
                                              max_extra_papers+1)
    for paper_idx in range(num_papers):
        paper = paper_type(f"paper-{paper_idx}")
        objects.add(paper)
        state.add(unpacked(paper))

    # Create goal
    goal_lits = [satisfied(loc) for loc in target_locs]
    goal = LiteralConjunction(goal_lits)

    filepath = os.path.join(PDDLDIR, problem_dir, problem_outfile)

    PDDLProblemParser.create_pddl_file(
        filepath,
        objects=objects,
        initial_state=state,
        problem_name="newspaper",
        domain_name=domain.domain_name,
        goal=goal,
        fast_downward_order=True,
    )
    print("Wrote out to {}.".format(filepath))

def generate_problems(problem_dir="newspapers"):
    domain = PDDLDomainParser(os.path.join(PDDLDIR, "newspapers.pddl"),
        expect_action_preds=False,
        operators_as_actions=True)

    train_problem_dir = problem_dir
    test_problem_dir = problem_dir + "_test"

    for problem_idx in range(50):
        if problem_idx < 40:
            problem_dir = train_problem_dir
        else:
            problem_dir = test_problem_dir
        if not os.path.exists(os.path.join(PDDLDIR, problem_dir)):
            os.makedirs(os.path.join(PDDLDIR, problem_dir))
        problem_outfile = "problem{}.pddl".format(problem_idx)

        num_locs = problem_idx+3
        sample_problem(domain, problem_dir, problem_outfile, num_locs)


if __name__ == "__main__":
    generate_problems()
