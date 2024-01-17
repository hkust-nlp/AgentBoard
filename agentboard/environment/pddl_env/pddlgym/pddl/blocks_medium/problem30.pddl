
(define (problem generatedblocks) (:domain blocks)
  (:objects
        b0 - block
	b1 - block
	b10 - block
	b11 - block
	b12 - block
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
	(clear b8)
	(handempty)
	(on b0 b1)
	(on b10 b11)
	(on b11 b12)
	(on b1 b2)
	(on b3 b4)
	(on b4 b5)
	(on b5 b6)
	(on b6 b7)
	(on b8 b9)
	(on b9 b10)
	(ontable b12)
	(ontable b2)
	(ontable b7)
  )
  (:goal (and
	(on b10 b8)
	(on b8 b6)
	(on b6 b12)
	(on b12 b1)
	(ontable b1)
	(on b5 b3)
	(on b3 b0)
	(on b0 b11)
	(on b11 b9)
	(ontable b9)
	(on b4 b2)
	(on b2 b7)
	(ontable b7)))
)
