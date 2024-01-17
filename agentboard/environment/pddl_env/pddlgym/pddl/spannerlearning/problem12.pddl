(define (problem 12) (:domain spanner) (:objects 
     bob - man
 spanner1 spanner2 spanner3 spanner4 spanner5 - spanner
     nut1 nut2 nut3 nut4 nut5 - nut
     location1 location2 location3 location4 location5 location6 - location
     shed gate - location
    ) (:init 
    (at bob shed)
    (at spanner1 location6)
    (useable spanner1)
    (at spanner2 location3)
    (useable spanner2)
    (at spanner3 location6)
    (useable spanner3)
    (at spanner4 location1)
    (useable spanner4)
    (at spanner5 location4)
    (useable spanner5)
    (loose nut1)
    (at nut1 gate)
    (loose nut2)
    (at nut2 gate)
    (loose nut3)
    (at nut3 gate)
    (loose nut4)
    (at nut4 gate)
    (loose nut5)
    (at nut5 gate)
    (link shed location1)
    (link location6 gate)
    (link location1 location2)
    (link location2 location3)
    (link location3 location4)
    (link location4 location5)
    (link location5 location6)
) (:goal
  (and
   (tightened nut1)
   (tightened nut2)
   (tightened nut3)
   (tightened nut4)
   (tightened nut5)
)))