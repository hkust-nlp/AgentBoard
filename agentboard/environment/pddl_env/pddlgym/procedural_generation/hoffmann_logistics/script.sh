#!/bin/bash
for i in {0..39}
do
    let "AIRS=5+($RANDOM%5)"
    let "CARS=2+($RANDOM%5)"
    let "CITY=1+($RANDOM%3)"
    let "PACKS=2+($RANDOM%5)"
   ./logistics -a $AIRS -c $CARS -s $CITY -p $PACKS > ../../pddl/manylogistics/problem$i.pddl
   echo "Generated logistics problem with $AIRS airplanes, $CARS cars, $CITY size cities, $PACKS packages."
done

for i in {40..49}
do
    let "AIRS=50+($RANDOM%5)"
    let "CARS=20+($RANDOM%5)"
    let "CITY=1+($RANDOM%3)"
    let "PACKS=20+($RANDOM%5)"
   ./logistics -a $AIRS -c $CARS -s $CITY -p $PACKS > ../../pddl/manylogistics_test/problem$i.pddl
   echo "Generated logistics problem with $AIRS airplanes, $CARS cars, $CITY size cities, $PACKS packages."
done
