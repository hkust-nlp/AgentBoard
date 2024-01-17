(define (problem rearrangement) 
    (:domain glibrearrangement)

    (:objects
    
	monkey-0 - moveable
	monkey-1 - moveable
	pawn-2 - moveable
	pawn-3 - moveable
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
    
	(ismonkey monkey-0)
	(ismonkey monkey-1)
	(ispawn pawn-2)
	(ispawn pawn-3)
	(isrobot robot)
	(at monkey-0 loc-0-1)
	(at monkey-1 loc-2-0)
	(at pawn-2 loc-2-0)
	(at pawn-3 loc-1-2)
	(at robot loc-1-1)
	(handsfree robot)

    ; action literals
    
	(pick monkey-0)
	(place monkey-0)
	(pick monkey-1)
	(place monkey-1)
	(pick pawn-2)
	(place pawn-2)
	(pick pawn-3)
	(place pawn-3)
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

    (:goal (and  (at pawn-3 loc-1-1)  (at monkey-1 loc-1-1) ))
)
    