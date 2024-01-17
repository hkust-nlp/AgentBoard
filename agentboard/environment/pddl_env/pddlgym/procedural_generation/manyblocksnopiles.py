from pddlgym.parser import PDDLDomainParser, PDDLProblemParser
from pddlgym.structs import LiteralConjunction
import pddlgym
import os
import numpy as np
np.random.seed(0)


PDDLDIR = os.path.join(os.path.dirname(pddlgym.__file__), "pddl")

def sample_blocks(domain, num_blocks):
    block_type = domain.types['block']
    ontable = domain.predicates['ontable']
    clear = domain.predicates['clear']
    handempty = domain.predicates['handempty']

    blocks = set()
    blocks_state = { handempty() }

    for block_num in range(num_blocks):
        block = block_type("b{}".format(block_num))
        blocks.add(block)
        blocks_state.update({clear(block), ontable(block)})

    return blocks, blocks_state

def create_goal(domain, objects, pile_heights):
    on = domain.predicates['on']
    ontable = domain.predicates['ontable']

    remaining_blocks = sorted(objects)

    goal_lits = []

    for pile_height in pile_heights:
        assert 2 < pile_height
        block_idxs = np.random.choice(len(remaining_blocks), size=pile_height, replace=False)
        blocks_in_pile = []
        for idx in block_idxs:
            blocks_in_pile.append(remaining_blocks[idx])
        remaining_blocks = [b for i, b in enumerate(remaining_blocks) if i not in block_idxs]
        # left is top
        for b1, b2 in zip(blocks_in_pile[:-1], blocks_in_pile[1:]):
            goal_lits.append(on(b1, b2))
        goal_lits.append(ontable(blocks_in_pile[-1]))

    return LiteralConjunction(goal_lits)

def sample_problem(domain, problem_dir, problem_outfile):
    

    blocks, block_state = sample_blocks(domain,
        num_blocks=np.random.randint(30, 61))

    goal = create_goal(domain, blocks, 
        pile_heights=np.random.randint(3, 7, 
            size=np.random.randint(1, 3)))

    objects = blocks
    initial_state = block_state

    filepath = os.path.join(PDDLDIR, problem_dir, problem_outfile)

    PDDLProblemParser.create_pddl_file(
        filepath,
        objects=objects,
        initial_state=initial_state,
        problem_name="manyblocksnopiles",
        domain_name=domain.domain_name,
        goal=goal,
        fast_downward_order=True,
    )
    print("Wrote out to {}.".format(filepath))

def generate_problems():
    domain = PDDLDomainParser(os.path.join(PDDLDIR, "manyblocksnopiles.pddl"),
        expect_action_preds=False,
        operators_as_actions=True)

    for problem_idx in range(50):
        if problem_idx < 40:
            problem_dir = "manyblocksnopiles"
        else:
            problem_dir = "manyblocksnopiles_test"
        problem_outfile = "problem{}.pddl".format(problem_idx)
        sample_problem(domain, problem_dir, problem_outfile)


if __name__ == "__main__":
    generate_problems()
