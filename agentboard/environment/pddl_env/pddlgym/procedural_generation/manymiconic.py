import random


def _get_str(num_floors, num_pass, num_buildings):
    mystr = "(define (problem miconicprob)\n\t(:domain miconic)\n\t(:objects\n"
    for bldg in range(num_buildings):
        for i in range(num_floors):
            mystr += "\t\tf{}_b{} - floor\n".format(i, bldg)
        for i in range(num_pass):
            mystr += "\t\tp{}_b{} - passenger\n".format(i, bldg)
    mystr += "\t)\n\n(:init\n"
    for bldg in range(num_buildings):
        for i in range(num_floors):
            for j in range(i+1, num_floors):
                mystr += "\t(above f{}_b{} f{}_b{})\n".format(i, bldg, j, bldg)
    mystr += "\n"
    for bldg in range(num_buildings):
        for i in range(num_pass):
            orig = random.randint(0, num_floors-1)
            while True:
                dest = random.randint(0, num_floors-1)
                if dest != orig:
                    break
            mystr += "\t(origin p{}_b{} f{}_b{})\n".format(i, bldg, orig, bldg)
            mystr += "\t(destin p{}_b{} f{}_b{})\n".format(i, bldg, dest, bldg)
    mystr += "\n"
    for bldg in range(num_buildings):
        mystr += "\t(lift-at f0_b{})\n".format(bldg)
    mystr += ")\n\n(:goal (and\n"
    for bldg in range(num_buildings):
        for i in range(num_pass):
            mystr += "\t(served p{}_b{})\n".format(i, bldg)
    mystr += "))"
    return mystr


def _main():
    # Train problems
    for i in range(40):
        num_floors = 10+random.randint(0, 10)
        num_pass = 1
        num_buildings = 3
        mystr = _get_str(num_floors, num_pass, num_buildings)
        with open("../pddl/manymiconic/problem{}.pddl".format(i), "w") as f:
            f.write(mystr)
    # Test problems
    for i in range(10):
        num_floors = 20+random.randint(0, 10)
        num_pass = 2
        num_buildings = 100
        mystr = _get_str(num_floors, num_pass, num_buildings)
        with open("../pddl/manymiconic_test/problem{}.pddl".format(i), "w") as f:
            f.write(mystr)


if __name__ == "__main__":
    _main()
