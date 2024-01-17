(define (domain desire)
(:types robot location - object)
(:constants  unknown - object
             desiree - robot)
(:predicates (loc ?o - object ?val - location))

(:action  move
          :parameters   (?from - location ?to - location)
          :precondition (loc desiree ?from)
          :effect  (and (not (loc desiree ?from))
                        (loc desiree ?to)))

(:action  set-loc-init
           :parameters    (?o - robot)
           :precondition  (loc ?o unknown)
           :effect        (not (loc ?o unknown)))
)
