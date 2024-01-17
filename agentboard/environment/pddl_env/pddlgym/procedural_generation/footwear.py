from pddlgym.parser import PDDLDomainParser, PDDLProblemParser
from pddlgym.structs import LiteralConjunction
import pddlgym
import os
import numpy as np
np.random.seed(0)


PDDLDIR = os.path.join(os.path.dirname(pddlgym.__file__), "pddl")

def sample_feet(domain):
    foot_type = domain.types['foot']
    isbare = domain.predicates['isbare']
    foot1 = foot_type('foot1')
    foot2 = foot_type('foot2')
    feet = { foot1, foot2 }
    feet_state = { isbare(foot1), isbare(foot2) }
    return feet, feet_state

def sample_socks(domain, num_pairs=20):
    sock_type = domain.types['sock']

    isblue = domain.predicates['isblue']
    isred = domain.predicates['isred']
    isstriped = domain.predicates['isstriped']
    isplain = domain.predicates['isplain']
    socksmatch = domain.predicates['socksmatch']
    sockfree = domain.predicates['sockfree']
    
    socks = set()
    socks_state = set()

    for pair in range(num_pairs):
        sock1 = sock_type("sock{}".format(2*pair))
        sock2 = sock_type("sock{}".format(2*pair + 1))
        socks.add(sock1)
        socks.add(sock2)
        socks_state.add(sockfree(sock1))
        socks_state.add(sockfree(sock2))
        socks_state.add(socksmatch(sock1,sock2))
        socks_state.add(socksmatch(sock2,sock1))
        if np.random.random() < 0.5:
            socks_state.add(isred(sock1))
            socks_state.add(isred(sock2))
        else:
            socks_state.add(isblue(sock1))
            socks_state.add(isblue(sock2))
        if np.random.random() < 0.5:
            socks_state.add(isstriped(sock1))
            socks_state.add(isstriped(sock2))
        else:
            socks_state.add(isplain(sock1))
            socks_state.add(isplain(sock2))

    return socks, socks_state

def sample_shoes(domain, num_pairs=20):
    shoe_type = domain.types['shoe']

    isdressshoe = domain.predicates['isdressshoe']
    issneaker = domain.predicates['issneaker']
    isboot = domain.predicates['isboot']
    issandle = domain.predicates['issandle']
    shoefree = domain.predicates['shoefree']
    shoeseq = domain.predicates['shoeseq']
    
    shoes = set()
    shoes_state = set()

    for pair in range(num_pairs):
        shoe1 = shoe_type("shoe{}".format(2*pair))
        shoe2 = shoe_type("shoe{}".format(2*pair + 1))
        shoes.add(shoe1)
        shoes.add(shoe2)
        shoes_state.add(shoefree(shoe1))
        shoes_state.add(shoefree(shoe2))
        shoes_state.add(shoeseq(shoe1, shoe1))
        shoes_state.add(shoeseq(shoe2, shoe2))
        rand = np.random.random()
        if rand < 0.25:
            shoes_state.add(isdressshoe(shoe1))
            shoes_state.add(isdressshoe(shoe2))
        elif rand < 0.5:
            shoes_state.add(isboot(shoe1))
            shoes_state.add(isboot(shoe2))
        elif rand < 0.75:
            shoes_state.add(issandle(shoe1))
            shoes_state.add(issandle(shoe2))
        else:
            shoes_state.add(issneaker(shoe1))
            shoes_state.add(issneaker(shoe2))

    return shoes, shoes_state

def sample_places(domain, num_places_per_type=2):
    place_type = domain.types['place']

    home_pred = domain.predicates['home']
    office_pred = domain.predicates['office']
    gym_pred = domain.predicates['gym']
    forest_pred = domain.predicates['forest']
    beach_pred = domain.predicates['beach']
    at = domain.predicates['at']

    places = set()
    places_state = set()

    home = place_type("home")
    places.add(home)
    places_state.add(home_pred(home))
    places_state.add(at(home))
    
    for i in range(num_places_per_type):
        office = place_type('office{}'.format(i))
        places.add(office)
        places_state.add(office_pred(office))

        gym = place_type('gym{}'.format(i))
        places.add(gym)
        places_state.add(gym_pred(gym))

        forest = place_type('forest{}'.format(i))
        places.add(forest)
        places_state.add(forest_pred(forest))

        beach = place_type('beach{}'.format(i))
        places.add(beach)
        places_state.add(beach_pred(beach))

    return places, places_state

def create_goal(domain, objects):
    place_type = domain.types['place']
    presentationdoneat = domain.predicates['presentationdoneat']
    workedoutat = domain.predicates['workedoutat']
    hikedat = domain.predicates['hikedat']
    swamat = domain.predicates['swamat']
    
    goal_lits = []

    while len(goal_lits) == 0:
        for obj in [o for o in objects if o.var_type == place_type]:
            if obj.startswith("office") and np.random.random() < 0.25:
                goal_lits.append(presentationdoneat(obj))
            elif obj.startswith("gym") and np.random.random() < 0.25:
                goal_lits.append(workedoutat(obj))
            elif obj.startswith("forest") and np.random.random() < 0.25:
                goal_lits.append(hikedat(obj))
            elif obj.startswith("beach") and np.random.random() < 0.25:
                goal_lits.append(swamat(obj))

    max_num_goal_lits = np.random.randint(1, 4)
    if len(goal_lits) > max_num_goal_lits:
        np.random.shuffle(goal_lits)
        goal_lits = goal_lits[:max_num_goal_lits]

    return LiteralConjunction(goal_lits)

def sample_problem(domain, problem_outfile):
    feet, feet_state = sample_feet(domain)
    socks, socks_state = sample_socks(domain, num_pairs=np.random.randint(10, 21))
    shoes, shoes_state = sample_shoes(domain, num_pairs=np.random.randint(10, 21))
    places, places_state = sample_places(domain, num_places_per_type=np.random.randint(5, 11))

    objects = feet | socks | shoes | places
    initial_state = feet_state | socks_state | shoes_state | places_state
    goal = create_goal(domain, objects)

    filepath = os.path.join(PDDLDIR, "footwear", problem_outfile)

    PDDLProblemParser.create_pddl_file(
        filepath,
        objects=objects,
        initial_state=initial_state,
        problem_name="footwear",
        domain_name=domain.domain_name,
        goal=goal,
        fast_downward_order=True,
    )
    print("Wrote out to {}.".format(filepath))

def generate_problems():
    domain = PDDLDomainParser(os.path.join(PDDLDIR, "footwear.pddl"),
        expect_action_preds=False,
        operators_as_actions=True)

    for problem_idx in range(50):
        problem_outfile = "problem{}.pddl".format(problem_idx)
        sample_problem(domain, problem_outfile)

if __name__ == "__main__":
    generate_problems()
