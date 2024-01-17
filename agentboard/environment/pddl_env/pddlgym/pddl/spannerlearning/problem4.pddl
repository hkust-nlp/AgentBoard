(define (problem 4) (:domain spanner) (:objects 
     bob - man
 spanner1 - spanner
     nut1 - nut
     location1 - location
     shed gate - location
    ) (:init 
    (at bob shed)
    (at spanner1 location1)
    (useable spanner1)
    (loose nut1)
    (at nut1 gate)
    (link shed location1)
    (link location1 gate)
) (:goal
  (and
   (tightened nut1)
)))
