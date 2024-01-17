
(define (problem prob) (:domain derivedblocks)
  (:objects
        block1 - obj
	block2 - obj
	gripper - robot
	table - loc
  )
  (:goal (and
	(gripper_empty gripper)
	(on_loc block1 table)
	(on_obj block2 block1)))
  (:init 
	(on_loc block2 table)
	(on_obj block1 block2)
))
