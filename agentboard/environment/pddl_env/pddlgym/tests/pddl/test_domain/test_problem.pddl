; this is a comment
(define (problem test-problem)
  (:domain test-domain)
  (:objects
    a1 - type1
    a2 - type1
    b1 - type1
    b2 - type1
    b3 - type1
    c1 - type2
    c2 - type2
    d1 - type2
    d2 - type2
    d3 - type2
  )

  (:init
    (pred1 b2)
    (pred2 c1)
    (pred3 a1 c1 d1)
    (pred3 a2 c2 d2)
    (actionpred a1)
    (actionpred a2)
    (actionpred b1)
    (actionpred b2)
    (actionpred b3)
  )

  (:goal (and
    (pred2 c2)
    (pred3 b1 c1 d1)
  ))
)
