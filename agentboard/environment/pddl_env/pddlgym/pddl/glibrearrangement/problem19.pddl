(define (problem rearrangement) 
    (:domain glibrearrangement)

    (:objects
    
	bear-0 - moveable
	monkey-1 - moveable
	pawn-2 - moveable
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
	(ismonkey monkey-1)
	(ispawn pawn-2)
	(isrobot robot)
	(at bear-0 loc-2-2)
	(at monkey-1 loc-1-1)
	(at pawn-2 loc-2-0)
	(at robot loc-0-2)
	(handsfree robot)

    ; action literals
    
	(pick bear-0)
	(place bear-0)
	(pick monkey-1)
	(place monkey-1)
	(pick pawn-2)
	(place pawn-2)
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

    (:goal (and  (holding bear-0)  (at pawn-2 loc-1-2) ))
)
    