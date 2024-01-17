(define (problem rearrangement) 
    (:domain glibrearrangement)

    (:objects
    
	bear-0 - moveable
	robot - moveable
	loc-0-0 - static
	loc-0-1 - static
	loc-0-2 - static
	loc-1-0 - static
	loc-1-1 - static
	loc-1-2 - static
	loc-2-0 - static
	loc-2-1 - static
	loc-2-2 - static
    )

    (:init
    
	(isbear bear-0)
	(isrobot robot)
	(at bear-0 loc-0-1)
	(at robot loc-0-2)
	(handsfree robot)

    ; action literals
    
	(pick bear-0)
	(place bear-0)
	(moveto loc-0-0)
	(moveto loc-0-1)
	(moveto loc-0-2)
	(moveto loc-1-0)
	(moveto loc-1-1)
	(moveto loc-1-2)
	(moveto loc-2-0)
	(moveto loc-2-1)
	(moveto loc-2-2)
    )

    (:goal (and  (at bear-0 loc-0-2) ))
)
    