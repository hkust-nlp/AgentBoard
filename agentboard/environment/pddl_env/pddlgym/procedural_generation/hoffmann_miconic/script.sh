#!/bin/bash
for i in {0..39}
do
    let "FLOORS=5+($RANDOM%25)"
    let "PASSES=3+($RANDOM%8)"
   ./miconic -f $FLOORS -p $PASSES > ../../pddl/manymiconic/problem$i.pddl
   echo "Generated miconic problem fill with $FLOORS floors and $PASSES passengers"
done

# for i in {40..49}
# do
#    ./miconic -f 250 -p 80 > ../../pddl/manymiconic_test/problem$i.pddl
# done
