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

def sample_problem(domain, problem_dir, problem_outfile, 
                   min_num_piles=30, max_num_piles=50,
                   min_num_piles_goal=1, max_num_piles_goal=2):
    
    blocks, block_state = sample_blocks(domain, 
        pile_heights=np.random.randint(1, 3, 
            size=np.random.randint(min_num_piles, max_num_piles+1)),
    )

    goal = create_goal(domain, blocks, 
        pile_heights=np.random.randint(2, 4, 
            size=np.random.randint(min_num_piles_goal, max_num_piles_goal+1)))

    objects = blocks
    initial_state = block_state

    filepath = os.path.join(PDDLDIR, problem_dir, problem_outfile)

    PDDLProblemParser.create_pddl_file(
        filepath,
        objects=objects,
        initial_state=initial_state,
        problem_name="manyblockssmallpiles",
        domain_name=domain.domain_name,
        goal=goal,
        fast_downward_order=True,
    )
    print("Wrote out to {}.".format(filepath))

def generate_problems():
    domain = PDDLDomainParser(os.path.join(PDDLDIR, "manyblockssmallpiles.pddl"),
        expect_action_preds=False,
        operators_as_actions=True)

    for problem_idx in range(50):
        if problem_idx < 40:
            problem_dir = "manyblockssmallpiles"
        else:
            problem_dir = "manyblockssmallpiles_test"
        problem_outfile = "problem{}.pddl".format(problem_idx)

        if problem_idx < 40:
            sample_problem(domain, problem_dir, problem_outfile, 
                   min_num_piles=10, max_num_piles=20,
                   min_num_piles_goal=1, max_num_piles_goal=2)
        else:
            sample_problem(domain, problem_dir, problem_outfile, 
                   min_num_piles=80, max_num_piles=100,
                   min_num_piles_goal=5, max_num_piles_goal=10)

if __name__ == "__main__":
    generate_problems()
