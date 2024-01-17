#!/bin/bash
for i in {0..39}
do
   ./grid -x 12 -y 12 -t 5 -k 55555 -l 55555 -p 25 > ../../pddl/manygrid/problem$i.pddl
done

for i in {40..49}
do
   ./grid -x 12 -y 12 -t 5 -k 55555 -l 55555 -p 25 > ../../pddl/manygrid_test/problem$i.pddl
done
