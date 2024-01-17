
(define (domain miconic)
  (:requirements :typing )
  (:types passenger floor)
  (:predicates (not-boarded ?v0 - passenger)
	(down ?v0 - floor)
	(boarded ?v0 - passenger)
	(depart ?v0 - floor ?v1 - passenger)
	(not-served ?v0 - passenger)
	(origin ?v0 - passenger ?v1 - floor)
	(board ?v0 - floor ?v1 - passenger)
	(lift-at ?v0 - floor)
	(served ?v0 - passenger)
	(destin ?v0 - passenger ?v1 - floor)
	(up ?v0 - floor)
	(above ?v0 - floor ?v1 - floor)
  )

  ; (:actions down up board depart)

  

	(:action down
		:parameters (?f1 - floor ?f2 - floor)
		:precondition (and (above ?f2 ?f1)
			(down ?f2)
			(lift-at ?f1))
		:effect (and
			(lift-at ?f2)
			(not (lift-at ?f1)))
	)
	

	(:action board
		:parameters (?f - floor ?p - passenger)
		:precondition (and (board ?f ?p)
			(lift-at ?f)
			(origin ?p ?f))
		:effect (and
			(boarded ?p))
	)
	

	(:action up
		:parameters (?f1 - floor ?f2 - floor)
		:precondition (and (above ?f1 ?f2)
			(lift-at ?f1)
			(up ?f2))
		:effect (and
			(lift-at ?f2)
			(not (lift-at ?f1)))
	)
	

	(:action depart
		:parameters (?f - floor ?p - passenger)
		:precondition (and (boarded ?p)
			(depart ?f ?p)
			(destin ?p ?f)
			(lift-at ?f))
		:effect (and
			(not (boarded ?p))
			(served ?p))
	)

)
        