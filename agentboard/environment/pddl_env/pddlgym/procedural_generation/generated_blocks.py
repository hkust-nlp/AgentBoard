from pddlgym.parser import PDDLDomainParser, PDDLProblemParser
from pddlgym.structs import LiteralConjunction
import pddlgym
import os
import numpy as np
from itertools import count
np.random.seed(0)


PDDLDIR = os.path.join(os.path.dirname(pddlgym.__file__), "pddl")

def sample_blocks(domain, pile_heights):
    block_type = domain.types['block']
    ontable = domain.predicates['ontable']
    clear = domain.predicates['clear']
    on = domain.predicates['on']
    handempty = domain.predicates['handempty']

    blocks = set()
    blocks_state = { handempty() }

    block_idx = count()
    for pile_height in pile_heights:
        assert pile_height >= 1
        blocks_in_pile = [block_type("b{}".format(next(block_idx))) \
            for _ in range(pile_height)]
        blocks.update(blocks_in_pile)
        # left is top
        if pile_height > 1:
            for b1, b2 in zip(blocks_in_pile[:-1], blocks_in_pile[1:]):
                blocks_state.add(on(b1, b2))
        blocks_state.add(ontable(blocks_in_pile[-1]))
        blocks_state.add(clear(blocks_in_pile[0]))

    return blocks, blocks_state

def create_goal(domain, objects, pile_heights):
    on = domain.predicates['on']
    ontable = domain.predicates['ontable']

    remaining_blocks = sorted(objects)

    goal_lits = []

    for pile_height in pile_heights:
        assert pile_height >= 1
        if len(remaining_blocks) < pile_height:
            if len(remaining_blocks) == 0:
                break
            pile_height = len(remaining_blocks)
        block_idxs = np.random.choice(len(remaining_blocks), size=pile_height, replace=False)
        blocks_in_pile = []
        for idx in block_idxs:
            blocks_in_pile.append(remaining_blocks[idx])
        remaining_blocks = [b for i, b in enumerate(remaining_blocks) if i not in block_idxs]
        # left is top
        if pile_height > 1:
            for b1, b2 in zip(blocks_in_pile[:-1], blocks_in_pile[1:]):
                goal_lits.append(on(b1, b2))
        goal_lits.append(ontable(blocks_in_pile[-1]))

    return LiteralConjunction(goal_lits)

def sample_problem(domain, problem_dir, problem_outfile, seen_problems,
                   min_num_piles=30, max_num_piles=50,
                   min_num_piles_goal=1, max_num_piles_goal=2,
                   min_pile_height=1, max_pile_height=3):

    while True:
        blocks, block_state = sample_blocks(domain, 
            pile_heights=np.random.randint(min_pile_height, max_pile_height, 
                size=np.random.randint(min_num_piles, max_num_piles+1)),
        )

        goal = create_goal(domain, blocks, 
            pile_heights=np.random.randint(min_pile_height, max_pile_height,
                size=np.random.randint(min_num_piles_goal, max_num_piles_goal+1)))

        objects = frozenset(blocks)
        initial_state = frozenset(block_state)

        if (initial_state, objects, goal) in seen_problems:
            continue

        seen_problems.add((initial_state, objects, goal))
        break

    filepath = os.path.join(PDDLDIR, problem_dir, problem_outfile)

    PDDLProblemParser.create_pddl_file(
        filepath,
        objects=objects,
        initial_state=initial_state,
        problem_name="generatedblocks",
        domain_name=domain.domain_name,
        goal=goal,
        fast_downward_order=True,
    )
    print("Wrote out to {}.".format(filepath))

def generate_problems(problem_dir="generated_blocks", min_num_piles=2, max_num_piles=5,
                      min_pile_height=1, max_pile_height=3):
    domain = PDDLDomainParser(os.path.join(PDDLDIR, "generated_blocks.pddl"),
        expect_action_preds=False,
        operators_as_actions=True)

    seen_problems = set()

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

        sample_problem(domain, problem_dir, problem_outfile, seen_problems, 
               min_num_piles=min_num_piles, max_num_piles=max_num_piles,
               min_num_piles_goal=min_num_piles, max_num_piles_goal=max_num_piles,
               min_pile_height=min_pile_height, max_pile_height=max_pile_height)


if __name__ == "__main__":
    # generate_problems()
    generate_problems(problem_dir="blocks_medium", min_num_piles=3, max_num_piles=6,
                      min_pile_height=3, max_pile_height=6)

