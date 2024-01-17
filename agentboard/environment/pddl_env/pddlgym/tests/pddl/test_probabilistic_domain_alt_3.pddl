; See https://github.com/tomsilver/pddlgym/issues/73

(define (domain tireworld)
  (:requirements :typing :strips :probabilistic-effects)
  (:types location)
  (:predicates
        (a)
        (b)
        (c)
       (test1)
       (test2)
  )

  ; (:actions test1 test2)

  (:action test1
    :parameters ()
    :precondition (and (a) (test1))
    :effect (and 
                (probabilistic 0.8 (and (not (a)) (b))
                               0.2 (and (not (a)) (c)))
  ))

  (:action test2
    :parameters ()
    :precondition (and (a) (test2))
    :effect (and 
                (not (a))
                (probabilistic 0.8 (and (b)) 0.2 (and (c)))
  ))
)