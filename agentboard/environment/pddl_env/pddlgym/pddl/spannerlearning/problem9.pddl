(define (problem 9) (:domain spanner) (:objects 
     bob - man
 spanner1 spanner2 spanner3 - spanner
     nut1 - nut
     location1 - location
     shed gate - location
    ) (:init 
    (at bob shed)
    (at spanner1 location1)
    (useable spanner1)
    (at spanner2 location1)
    (useable spanner2)
    (at spanner3 location1)
    (useable spanner3)
    (loose nut1)
    (at nut1 gate)
    (link shed location1)
    (link location1 gate)
) (:goal
  (and
   (tightened nut1)
)))