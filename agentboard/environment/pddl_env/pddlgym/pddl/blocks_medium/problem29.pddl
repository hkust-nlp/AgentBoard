
(define (problem generatedblocks) (:domain blocks)
  (:objects
        b0 - block
	b1 - block
	b10 - block
	b11 - block
	b12 - block
	b13 - block
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
	(clear b10)
	(clear b5)
	(handempty)
	(on b0 b1)
	(on b10 b11)
	(on b11 b12)
	(on b12 b13)
	(on b1 b2)
	(on b2 b3)
	(on b3 b4)
	(on b5 b6)
	(on b6 b7)
	(on b7 b8)
	(on b8 b9)
	(ontable b13)
	(ontable b4)
	(ontable b9)
  )
  (:goal (and
	(on b1 b2)
	(on b2 b8)
	(on b8 b6)
	(ontable b6)
	(on b12 b0)
	(on b0 b7)
	(ontable b7)
	(on b5 b10)
	(on b10 b9)
	(ontable b9)))
)
