(define (problem doors) 
    (:domain doors)

    (:objects
    key-0 - key
	key-1 - key
	loc-0-0 - location
	loc-0-1 - location
	loc-0-2 - location
	loc-0-3 - location
	loc-1-0 - location
	loc-1-1 - location
	loc-1-2 - location
	loc-1-3 - location
	loc-10-0 - location
	loc-10-1 - location
	loc-10-2 - location
	loc-10-3 - location
	loc-11-0 - location
	loc-11-1 - location
	loc-11-2 - location
	loc-11-3 - location
	loc-2-0 - location
	loc-2-1 - location
	loc-2-2 - location
	loc-2-3 - location
	loc-3-0 - location
	loc-3-1 - location
	loc-3-2 - location
	loc-3-3 - location
	loc-4-0 - location
	loc-4-1 - location
	loc-4-2 - location
	loc-4-3 - location
	loc-5-0 - location
	loc-5-1 - location
	loc-5-2 - location
	loc-5-3 - location
	loc-6-0 - location
	loc-6-1 - location
	loc-6-2 - location
	loc-6-3 - location
	loc-7-0 - location
	loc-7-1 - location
	loc-7-2 - location
	loc-7-3 - location
	loc-8-0 - location
	loc-8-1 - location
	loc-8-2 - location
	loc-8-3 - location
	loc-9-0 - location
	loc-9-1 - location
	loc-9-2 - location
	loc-9-3 - location
	room-0 - room
	room-1 - room
	room-2 - room
    )

    (:init
    (at loc-0-0)
	(unlocked room-0)
	(locinroom loc-0-0 room-0)
	(moveto loc-0-0)
	(locinroom loc-0-1 room-0)
	(moveto loc-0-1)
	(locinroom loc-0-2 room-0)
	(moveto loc-0-2)
	(locinroom loc-0-3 room-0)
	(moveto loc-0-3)
	(locinroom loc-1-0 room-0)
	(moveto loc-1-0)
	(locinroom loc-1-1 room-0)
	(moveto loc-1-1)
	(locinroom loc-1-2 room-0)
	(moveto loc-1-2)
	(locinroom loc-1-3 room-0)
	(moveto loc-1-3)
	(locinroom loc-2-0 room-0)
	(moveto loc-2-0)
	(locinroom loc-2-1 room-0)
	(moveto loc-2-1)
	(locinroom loc-2-2 room-0)
	(moveto loc-2-2)
	(locinroom loc-2-3 room-0)
	(moveto loc-2-3)
	(locinroom loc-3-0 room-0)
	(moveto loc-3-0)
	(locinroom loc-3-1 room-0)
	(moveto loc-3-1)
	(locinroom loc-3-2 room-0)
	(moveto loc-3-2)
	(locinroom loc-3-3 room-0)
	(moveto loc-3-3)
	(locinroom loc-4-0 room-1)
	(moveto loc-4-0)
	(locinroom loc-4-1 room-1)
	(moveto loc-4-1)
	(locinroom loc-4-2 room-1)
	(moveto loc-4-2)
	(locinroom loc-4-3 room-1)
	(moveto loc-4-3)
	(locinroom loc-5-0 room-1)
	(moveto loc-5-0)
	(locinroom loc-5-1 room-1)
	(moveto loc-5-1)
	(locinroom loc-5-2 room-1)
	(moveto loc-5-2)
	(locinroom loc-5-3 room-1)
	(moveto loc-5-3)
	(locinroom loc-6-0 room-1)
	(moveto loc-6-0)
	(locinroom loc-6-1 room-1)
	(moveto loc-6-1)
	(locinroom loc-6-2 room-1)
	(moveto loc-6-2)
	(locinroom loc-6-3 room-1)
	(moveto loc-6-3)
	(locinroom loc-7-0 room-1)
	(moveto loc-7-0)
	(locinroom loc-7-1 room-1)
	(moveto loc-7-1)
	(locinroom loc-7-2 room-1)
	(moveto loc-7-2)
	(locinroom loc-7-3 room-1)
	(moveto loc-7-3)
	(locinroom loc-8-0 room-2)
	(moveto loc-8-0)
	(locinroom loc-8-1 room-2)
	(moveto loc-8-1)
	(locinroom loc-8-2 room-2)
	(moveto loc-8-2)
	(locinroom loc-8-3 room-2)
	(moveto loc-8-3)
	(locinroom loc-9-0 room-2)
	(moveto loc-9-0)
	(locinroom loc-9-1 room-2)
	(moveto loc-9-1)
	(locinroom loc-9-2 room-2)
	(moveto loc-9-2)
	(locinroom loc-9-3 room-2)
	(moveto loc-9-3)
	(locinroom loc-10-0 room-2)
	(moveto loc-10-0)
	(locinroom loc-10-1 room-2)
	(moveto loc-10-1)
	(locinroom loc-10-2 room-2)
	(moveto loc-10-2)
	(locinroom loc-10-3 room-2)
	(moveto loc-10-3)
	(locinroom loc-11-0 room-2)
	(moveto loc-11-0)
	(locinroom loc-11-1 room-2)
	(moveto loc-11-1)
	(locinroom loc-11-2 room-2)
	(moveto loc-11-2)
	(locinroom loc-11-3 room-2)
	(moveto loc-11-3)
	(keyforroom key-0 room-1)
	(keyat key-0 loc-3-2)
	(pick key-0)
	(keyforroom key-1 room-2)
	(keyat key-1 loc-6-2)
	(pick key-1)

    )

    (:goal (and (at loc-11-3)))
)
    