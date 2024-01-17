
(define (domain derivedblocks)
  (:requirements :typing)
  (:types loc obj robot)
  
  (:predicates (on_loc ?v0 - obj ?v1 - loc)
	(on_obj ?v0 - obj ?v1 - obj)
	(in_gripper ?v0 - obj ?v1 - robot)
	(obj_clear ?v0 - obj)
	(gripper_empty ?v0 - robot)
	(pick ?v0 - obj)
	(place ?v0 - loc)
	(stack ?v0 - obj)
  )
  ; (:actions stack pick place)

  

	(:action pick_from_loc
		:parameters (?o1 - obj ?l - loc ?r - robot)
		:precondition (and (pick ?o1)
			(gripper_empty ?r)
			(obj_clear ?o1)
			(on_loc ?o1 ?l))
		:effect (and
			(in_gripper ?o1 ?r)
			(not (on_loc ?o1 ?l)))
	)
	

	(:action place_on_loc
		:parameters (?o1 - obj ?l - loc ?r - robot)
		:precondition (and (place ?l)
			(in_gripper ?o1 ?r))
		:effect (and
			(not (in_gripper ?o1 ?r))
			(on_loc ?o1 ?l))
	)
	

	(:action unstack
		:parameters (?o1 - obj ?o2 - obj ?r - robot)
		:precondition (and (pick ?o1)
			(gripper_empty ?r)
			(obj_clear ?o1)
			(on_obj ?o1 ?o2))
		:effect (and
			(in_gripper ?o1 ?r)
			(not (on_obj ?o1 ?o2)))
	)
	

	(:action stack
		:parameters (?o1 - obj ?o2 - obj ?r - robot)
		:precondition (and (stack ?o2)
			(in_gripper ?o1 ?r)
			(obj_clear ?o2))
		:effect (and
			(not (in_gripper ?o1 ?r))
			(on_obj ?o1 ?o2))
	)

  (:derived (obj_clear ?v_1) (forall (?o - obj) (not (on_obj ?o ?v_1))))

(:derived (gripper_empty ?v_1) (forall (?o - obj) (not (in_gripper ?o ?v_1))))



)
        