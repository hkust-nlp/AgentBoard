#!/bin/bash
# for i in {0..39}
# do
#     let "LOCS=10+($RANDOM%5)"
#     let "CARS=3+($RANDOM%5)"
#     ./ferry -l $LOCS -c $CARS > ../../pddl/manyferry/problem$i.pddl
#     echo "Generated ferry problem with $LOCS locations, $CARS cars."
# done

for i in {40..49}
do
    let "LOCS=250+($RANDOM%20)"
    let "CARS=50+($RANDOM%20)"
    ./ferry -l $LOCS -c $CARS > ../../pddl/manyferry_test/problem$i.pddl
    echo "Generated ferry problem with $LOCS locations, $CARS cars."
done
