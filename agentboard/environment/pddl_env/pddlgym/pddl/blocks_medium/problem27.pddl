
(define (problem generatedblocks) (:domain blocks)
  (:objects
        b0 - block
	b1 - block
	b10 - block
	b2 - block
	b3 - block
	b4 - block
	b5 - block
	b6 - block
	b7 - block
	b8 - block
	b9 - block
  )
  (:init 
	(clear b0)
	(clear b3)
	(clear b6)
	(handempty)
	(on b0 b1)
	(on b1 b2)
	(on b3 b4)
	(on b4 b5)
	(on b6 b7)
	(on b7 b8)
	(on b8 b9)
	(on b9 b10)
	(ontable b10)
	(ontable b2)
	(ontable b5)
  )
  (:goal (and
	(on b3 b10)
	(on b10 b6)
	(on b6 b9)
	(on b9 b5)
	(ontable b5)
	(on b8 b4)
	(on b4 b2)
	(on b2 b0)
	(ontable b0)
	(on b1 b7)
	(ontable b7)))
)
