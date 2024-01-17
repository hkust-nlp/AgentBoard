
(define (domain minecraft)
  (:requirements :strips :typing)
  (:types moveable static agent)
  (:predicates
    (isgrass ?arg0 - moveable)
	(islog ?arg0 - moveable)
	(isplanks ?arg0 - moveable)
	(at ?arg0 - moveable ?arg1 - static)
	(agentat ?arg0 - static)
	(inventory ?arg0 - moveable)
	(hypothetical ?arg0 - moveable)
	(equipped ?arg0 - moveable ?arg1 - agent)
    (handsfree ?arg0 - agent)
    (recall ?arg0 - moveable)
    (move ?arg0 - static)
    (craftplank ?arg0 - moveable ?arg1 - moveable)
    (equip ?arg0 - moveable)
    (pick ?arg0 - moveable)
  )

  ; (:actions recall move craftplank equip pick)

	(:action recall
		:parameters (?var0 - moveable ?var1 - agent)
		:precondition (and
            (recall ?var0)
			(equipped ?var0 ?var1)
		)
		:effect (and
			(inventory ?var0)
			(not (equipped ?var0 ?var1))
            (handsfree ?var1)
		)
	)

	(:action move
		:parameters (?var0 - static ?var1 - static)
		:precondition (and
            (move ?var0)
			(agentat ?var1)
		)
		:effect (and
			(agentat ?var0)
			(not (agentat ?var1))
		)
	)

	(:action craftplank
		:parameters (?var0 - moveable ?var1 - agent ?var2 - moveable)
		:precondition (and
            (craftplank ?var0 ?var2)
			(hypothetical ?var0)
			(islog ?var2)
			(equipped ?var2 ?var1)
		)
		:effect (and
			(inventory ?var0)
			(isplanks ?var0)
            (handsfree ?var1)
			(not (equipped ?var2 ?var1))
			(not (hypothetical ?var0))
			(not (islog ?var2))
		)
	)

	(:action equip
		:parameters (?var0 - moveable ?var1 - agent)
		:precondition (and
            (equip ?var0)
			(inventory ?var0)
			(handsfree ?var1)
		)
		:effect (and
			(equipped ?var0 ?var1)
            (not (handsfree ?var1))
			(not (inventory ?var0))
		)
	)

	(:action pick
		:parameters (?var0 - moveable ?var1 - static)
		:precondition (and
            (pick ?var0)
			(at ?var0 ?var1)
			(agentat ?var1)
		)
		:effect (and
			(inventory ?var0)
			(not (at ?var0 ?var1))
		)
	))