from pddlgym.parser import PDDLDomainParser, PDDLProblemParser
from pddlgym.structs import LiteralConjunction
import pddlgym
import os
import numpy as np
import time
from itertools import count
np.random.seed(0)


PDDLDIR = os.path.join(os.path.dirname(pddlgym.__file__), "pddl")


def sample_problem(domain, problem_dir, problem_outfile, maze_array):
    loc_type = domain.types['location']
    player_type = domain.types['player']

    at = domain.predicates['at']
    clear = domain.predicates['clear']
    move_dir_down = domain.predicates['move-dir-down']
    move_dir_left = domain.predicates['move-dir-left']
    move_dir_right = domain.predicates['move-dir-right']
    move_dir_up = domain.predicates['move-dir-up']
    oriented_down = domain.predicates['oriented-down']
    oriented_left = domain.predicates['oriented-left']
    oriented_right = domain.predicates['oriented-right']
    oriented_up = domain.predicates['oriented-up']
    is_goal = domain.predicates['is-goal']

    # Create objects and state
    state = set()
    objects = set()
    goal = None
    
    player = player_type("player-1")
    objects.add(player)
    state.add(np.random.choice([oriented_down, oriented_left, oriented_right, oriented_up])(player))
    
    
    for r in range(len(maze_array)):
        for c in range(len(maze_array[r])):
            loc = loc_type(f"loc-{r+1}-{c+1}")
            objects.add(loc)

            if maze_array[r][c] == 0: #empty: clear
                state.add(clear(loc))
            elif maze_array[r][c] == 1: #blocked: 
                pass
            elif maze_array[r][c] == 2: #player init: at
                state.add(at(player, loc))
            else: #goal: clear (should be 3)
                goal = at(player, loc)
                state.add(clear(loc))
                state.add(is_goal(loc))
            

    for r in range(1, len(maze_array)-1):
        for c in range(1, len(maze_array[r])-1):
            if maze_array[r][c] == 1:
                continue
            if maze_array[r-1][c] != 1:
                state.add(move_dir_up(loc_type(f"loc-{r+1}-{c+1}"), loc_type(f"loc-{r}-{c+1}")))
            if maze_array[r+1][c] != 1:
                state.add(move_dir_down(loc_type(f"loc-{r+1}-{c+1}"), loc_type(f"loc-{r+2}-{c+1}")))
            if maze_array[r][c-1] != 1:
                state.add(move_dir_left(loc_type(f"loc-{r+1}-{c+1}"), loc_type(f"loc-{r+1}-{c}")))
            if maze_array[r][c+1] != 1:
                state.add(move_dir_right(loc_type(f"loc-{r+1}-{c+1}"), loc_type(f"loc-{r+1}-{c+2}")))

    filepath = os.path.join(PDDLDIR, problem_dir, problem_outfile)

    PDDLProblemParser.create_pddl_file(
        filepath,
        objects=objects,
        initial_state=state,
        problem_name="maze",
        domain_name=domain.domain_name,
        goal=goal,
        fast_downward_order=True,
    )
    print("Wrote out to {}.".format(filepath))

def generate_problems(problem_dir="maze"):
    domain = PDDLDomainParser(os.path.join(PDDLDIR, "maze.pddl"),
        expect_action_preds=False,
        operators_as_actions=True)

    train_problem_dir = problem_dir
    test_problem_dir = problem_dir + "_test"

    for problem_idx in range(0, 50):
        if problem_idx < 40:
            problem_dir = train_problem_dir
        else:
            problem_dir = test_problem_dir
        if not os.path.exists(os.path.join(PDDLDIR, problem_dir)):
            os.makedirs(os.path.join(PDDLDIR, problem_dir))
        problem_outfile = "problem{}.pddl".format(problem_idx)
        
        min_maze_sizes = [6, 10, 20, 30, 40]
        max_maze_sizes = [10, 20, 30, 40, 50]
        maze_size_index = problem_idx//10
        maze_size = np.random.randint(min_maze_sizes[maze_size_index], max_maze_sizes[maze_size_index])

        maze_array = generate_maze_wilsons(maze_size)
        display(maze_array) 
        sample_problem(domain, problem_dir, problem_outfile, maze_array)


def generate_maze_wilsons(n):
    maze_array = [[1 if c == 0 or c == n-1 or r == 0 or r == n-1 else 4 for c in range(n)] for r in range(n)] #Borders are blocked (4 is place-holder for Wilson's)

    start_of_maze = (np.random.randint(1, n-1), np.random.randint(1, n-1))
    maze_array[start_of_maze[0]][start_of_maze[1]] = 0

    in_maze = {start_of_maze}
    valid_additions = get_valid_additions(maze_array)
    old_valid_additions = set()

    dead_ends = set()
    
    while len(valid_additions) > 0 and (valid_additions != old_valid_additions): 
        old_valid_additions = valid_additions
        maze_array, in_maze, new_dead_ends = get_loop_erased_random_walk(n, maze_array, in_maze, valid_additions)
        dead_ends = dead_ends | new_dead_ends 
        valid_additions = get_valid_additions(maze_array) - dead_ends
    
    empty_locations = []
    for r in range(n):
        for c in range(n):
            if maze_array[r][c] == 4:
                maze_array[r][c] = 1
            elif maze_array[r][c] == 0:
                empty_locations.append((r,c))

    player_coord_ind, goal_coord_ind = np.random.randint(0, len(empty_locations), 2)
    while player_coord_ind == goal_coord_ind:
        goal_coord_ind = np.random.randint(0, len(empty_locations))
    player_coord = empty_locations[player_coord_ind]
    goal_coord = empty_locations[goal_coord_ind]

    maze_array[player_coord[0]][player_coord[1]] = 2
    maze_array[goal_coord[0]][goal_coord[1]] = 3
    
    return maze_array


def get_loop_erased_random_walk(n, maze_array, in_maze, valid_additions):
    curr = tuple(valid_additions)[np.random.randint(len(valid_additions))]

    adjacent_to_maze = set(get_inbound_neighbors(curr, maze_array)) & in_maze

    assert len(adjacent_to_maze) == 0 or len(adjacent_to_maze) == 1 #Because curr is chosen from valid_additions, should be 1 or 0

    walk = [curr]
    visited = {curr}
    dead_ends = set()

    while len(adjacent_to_maze) != 1:
        valid_neighbors = list((set(get_inbound_neighbors(curr, maze_array)) - visited - dead_ends) & valid_additions) #Neighbor should only connect to existing maze at one edge

        if len(valid_neighbors) == 0: #No valid neighbors, add curr to set of dead ends
            dead_ends.add(curr)
            visited.remove(walk.pop())
            if len(walk) == 0:
                return maze_array, in_maze, dead_ends
            else:
                curr = walk[len(walk)-1]
                continue

        neighbor = valid_neighbors[np.random.choice(len(valid_neighbors))]

        neighbors_of_neighbor = set(get_inbound_neighbors(neighbor, maze_array))
        adjacent = (neighbors_of_neighbor - {curr}) & visited
        if len(adjacent) > 0: #If cycle (by being in adjacent), remove elements of cycle, and reset curr
            while walk[len(walk)-1] not in adjacent:
                visited.remove(walk.pop())
            curr = walk[len(walk)-1]
        else:
            curr = neighbor
            walk.append(curr)
            visited.add(curr)
            adjacent_to_maze = set(get_inbound_neighbors(curr, maze_array)) & in_maze

    #Add random walk to maze and remove from unvisited set
    for (row, col) in walk:
        maze_array[row][col] = 0

    in_maze = in_maze | visited
    return maze_array, in_maze, set() #Dead-ends should be empty set since the elements possibly in dead-ends can be used otherwise?


def get_inbound_neighbors(coords, maze_array):
    valid_neighbors = []
    if maze_array[coords[0]-1][coords[1]] != 1:
        valid_neighbors.append((coords[0]-1, coords[1]))
    if maze_array[coords[0]+1][coords[1]] != 1:
        valid_neighbors.append((coords[0]+1, coords[1]))
    if maze_array[coords[0]][coords[1]-1] != 1:
        valid_neighbors.append((coords[0], coords[1]-1))
    if maze_array[coords[0]][coords[1]+1] != 1:
        valid_neighbors.append((coords[0], coords[1]+1))
    return valid_neighbors

def get_valid_additions(maze_array):
    adjacent_valid_additions = set()
    for r in range(1, len(maze_array)-1):
        for c in range(1, len(maze_array)-1):
            adjacent_maze_edges = 0
            if maze_array[r-1][c] == 0:
                adjacent_maze_edges += 1
            if maze_array[r+1][c] == 0:
                adjacent_maze_edges += 1
            if maze_array[r][c-1] == 0:
                adjacent_maze_edges += 1
            if maze_array[r][c+1] == 0:
                adjacent_maze_edges += 1
            if adjacent_maze_edges <= 1 and maze_array[r][c] == 4:
                adjacent_valid_additions.add((r,c))
    
    valid_additions = set()
    for (r, c) in adjacent_valid_additions:
        valid_neighbors = 0
        if (r-1, c) in adjacent_valid_additions or maze_array[r-1][c] == 0:
            valid_neighbors += 1
        if (r+1, c) in adjacent_valid_additions or maze_array[r+1][c] == 0:
            valid_neighbors += 1
        if (r, c-1) in adjacent_valid_additions or maze_array[r][c-1] == 0:
            valid_neighbors += 1
        if (r, c+1) in adjacent_valid_additions or maze_array[r][c+1] == 0:
            valid_neighbors += 1
        if valid_neighbors != 0:
            valid_additions.add((r,c)) 
        
    return valid_additions


def display(maze_array):
    print('/', '\t', [(i+1)%10 for i in range(len(maze_array))])
    for i in range(len(maze_array)):
        print(i+1, '\t', maze_array[i])
    print("----------------------")


if __name__ == "__main__":
    generate_problems()

"""
Maze-generation algorithm: https://en.wikipedia.org/wiki/Maze_generation_algorithm
0 is empty space, 1 is wall, 2 is Start, 3 is Goal
Requirements: player start is not goal, surroundings must be 1 (blocked off), goal is reachable
"""
