; this is a comment
(define (domain test-probabilistic-domain-alt-2)
  (:requirements :typing :probabilistic-effects)
  (:types type1 type2)
  (:predicates (pred1 ?x - type1)
               (pred2 ?x - type2)
               (pred3 ?x - type1 ?y - type2 ?z - type2)
               (actionpred ?x - type1)
  )

  ; (:actions actionpred)
(and 
  (:action action1
   :parameters (?a - type1 ?b - type1 ?c - type2 ?d - type2)
   :precondition (and (actionpred ?b)
                      (pred1 ?b)
                      (pred3 ?a ?c ?d)
                      (pred2 ?c)
                      )
   :effect       (and 
                      (probabilistic
                        0.5  (and (not (pred2 ?c)))
                        0.4  (and (not (pred1 ?b)))
                        0.1 (and (pred3 ?b ?d ?c))))
   )
)
