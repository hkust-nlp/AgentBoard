(define (problem 1) (:domain spanner) (:objects 
     bob - man
 spanner1 - spanner
     nut1 - nut
     location1 location2 - location
     shed gate - location
    ) (:init 
    (at bob shed)
    (at spanner1 location1)
    (useable spanner1)
    (loose nut1)
    (at nut1 gate)
    (link shed location1)
    (link location2 gate)
    (link location1 location2)
) (:goal
  (and
   (tightened nut1)
)))
