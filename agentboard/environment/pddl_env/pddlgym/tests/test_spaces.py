from pddlgym.parser import PDDLDomainParser, PDDLProblemParser
from pddlgym.structs import Predicate, Literal, Type, Not, Anti, LiteralConjunction, State
from pddlgym.spaces import LiteralSpace
from pddlgym.core import PDDLEnv

import os
import time
import unittest


class TestSpaces(unittest.TestCase):
    def test_hierarchical_spaces(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        domain_file = os.path.join(dir_path, 'pddl', 'hierarchical_type_test_domain.pddl')
        problem_file = os.path.join(dir_path, 'pddl', 'hierarchical_type_test_domain', 
            'hierarchical_type_test_problem.pddl')
        domain = PDDLDomainParser(domain_file)
        problem = PDDLProblemParser(problem_file, domain.domain_name, domain.types,
            domain.predicates, domain.actions)
        actions = list(domain.actions)
        action_predicates = [domain.predicates[a] for a in actions]

        space = LiteralSpace(set(domain.predicates.values()) - set(action_predicates),
            type_to_parent_types=domain.type_to_parent_types)
        all_ground_literals = space.all_ground_literals(State(problem.initial_state, 
            problem.objects, problem.goal))

        ispresent = Predicate("ispresent", 1, [Type("entity")])
        islight = Predicate("islight", 1, [Type("object")])
        isfurry = Predicate("isfurry", 1, [Type("animal")])
        ishappy = Predicate("ishappy", 1, [Type("animal")])
        attending = Predicate("attending", 2, [Type("animal"), Type("object")])

        nomsy = Type("jindo")("nomsy")
        rover = Type("corgi")("rover")
        rene = Type("cat")("rene")
        block1 = Type("block")("block1")
        block2 = Type("block")("block2")
        cylinder1 = Type("cylinder")("cylinder1")

        assert all_ground_literals == {
            ispresent(nomsy),
            ispresent(rover),
            ispresent(rene),
            ispresent(block1),
            ispresent(block2),
            ispresent(cylinder1),
            islight(block1),
            islight(block2),
            islight(cylinder1),
            isfurry(nomsy),
            isfurry(rover),
            isfurry(rene),
            ishappy(nomsy),
            ishappy(rover),
            ishappy(rene),
            attending(nomsy, block1),
            attending(nomsy, block2),
            attending(nomsy, cylinder1),
            attending(rover, block1),
            attending(rover, block2),
            attending(rover, cylinder1),
            attending(rene, block1),
            attending(rene, block2),
            attending(rene, cylinder1),
        }



    def test_dynamic_action_space(self, verbose=False):
        """
        """
        dir_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "pddl")

        for name in [
                # "Manymiconic",
                # "Manygripper",
                "Blocks_operator_actions",
                "Hanoi_operator_actions",
            ]:
            domain_file = os.path.join(dir_path, "{}.pddl".format(name.lower()))
            problem_dir = os.path.join(dir_path, name.lower())
            # problem_dir = os.path.join(dir_path, name.lower()+"_test")

            env1 = PDDLEnv(domain_file, problem_dir,
                operators_as_actions=True,
                dynamic_action_space=False,
            )

            env2 = PDDLEnv(domain_file, problem_dir,
                operators_as_actions=True,
                dynamic_action_space=True,
            )

            env1.action_space.seed(0)
            env2.action_space.seed(0)
            state1, _ = env1.reset()
            state2, _ = env2.reset()
            assert state1 == state2

            for _ in range(25):
                start_time = time.time()
                valid_actions1 = env1.action_space.all_ground_literals(state1)
                if verbose:
                    print("Computing valid action spaces without instantiator took {} seconds".format(
                        time.time() - start_time))
                start_time = time.time()
                valid_actions2 = env2.action_space.all_ground_literals(state2)
                if verbose:
                    print("Computing valid action spaces *with* instantiator took {} seconds".format(
                        time.time() - start_time))
                assert valid_actions2.issubset(valid_actions1)
                action = env2.action_space.sample(state2)
                state1, _, _, _ = env1.step(action)
                state2, _, _, _ = env2.step(action)

            if verbose:
                print("Test passed for environment {}.".format(name))



    def test_dynamic_action_space_same_obj(self):
        """
        """
        dir_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "pddl")

        name = "dynamic_action_space_same_obj"
        domain_file = os.path.join(dir_path, "{}.pddl".format(name.lower()))
        problem_dir = os.path.join(dir_path, name.lower())

        env = PDDLEnv(domain_file, problem_dir,
            operators_as_actions=True,
            dynamic_action_space=True,
        )
        assert len(env.problems) == 2  # both problems have the same object set

        env.fix_problem_index(0)
        state1, _ = env.reset()
        # Only one action is possible: unstack(a, b)
        for _ in range(25):
            act1 = env.action_space.sample(state1)
            assert act1.predicate.name == "unstack"
            assert act1.variables[0].name == "a"
            assert act1.variables[1].name == "b"

        env.fix_problem_index(1)
        state2, _ = env.reset()
        assert state1.objects == state2.objects
        # Only one action is possible: unstack(d, c)
        for _ in range(25):
            act2 = env.action_space.sample(state2)
            assert act2.predicate.name == "unstack"
            assert act2.variables[0].name == "d"
            assert act2.variables[1].name == "c"



if __name__ == "__main__":
    unittest.main()
