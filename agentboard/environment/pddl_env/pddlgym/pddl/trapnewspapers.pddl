(define (domain trapnewspapers)
    (:requirements :strips :typing)
    (:types loc paper)
    (:predicates 
        (at ?loc - loc)
        (isHomeBase ?loc - loc)
        (satisfied ?loc - loc)
        (wantsPaper ?loc - loc)
        (safe ?loc - loc)
        (unpacked ?paper - paper)
        (carrying ?paper - paper)
    )
    
    (:action pick-up
        :parameters (?paper - paper ?loc - loc)
        :precondition (and
            (at ?loc)
            (isHomeBase ?loc)
            (unpacked ?paper)
        )
        :effect (and
            (not (unpacked ?paper))
            (carrying ?paper)
        )
    )
    
    (:action move
        :parameters (?from - loc ?to - loc)
        :precondition (and
            (at ?from)
            (safe ?from)
        )
        :effect (and
            (not (at ?from))
            (at ?to)
        )
    )
    
    (:action deliver
        :parameters (?paper - paper ?loc - loc)
        :precondition (and
            (at ?loc)
            (carrying ?paper)
        )
        :effect (and
            (not (carrying ?paper))
            (not (wantsPaper ?loc))
            (satisfied ?loc)
        )
    )
    
)
