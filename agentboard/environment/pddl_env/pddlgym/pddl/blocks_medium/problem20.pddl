
(define (problem generatedblocks) (:domain blocks)
  (:objects
        b0 - block
	b1 - block
	b10 - block
	b11 - block
	b12 - block
	b13 - block
	b14 - block
	b15 - block
	b16 - block
	b17 - block
	b18 - block
	b19 - block
	b2 - block
	b20 - block
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
	(clear b15)
	(clear b18)
	(clear b3)
	(clear b6)
	(handempty)
	(on b0 b1)
	(on b10 b11)
	(on b11 b12)
	(on b12 b13)
	(on b13 b14)
	(on b15 b16)
	(on b16 b17)
	(on b18 b19)
	(on b19 b20)
	(on b1 b2)
	(on b3 b4)
	(on b4 b5)
	(on b6 b7)
	(on b7 b8)
	(on b8 b9)
	(ontable b14)
	(ontable b17)
	(ontable b20)
	(ontable b2)
	(ontable b5)
	(ontable b9)
  )
  (:goal (and
	(on b5 b11)
	(on b11 b13)
	(on b13 b6)
	(on b6 b14)
	(ontable b14)
	(on b12 b7)
	(on b7 b18)
	(on b18 b8)
	(on b8 b19)
	(ontable b19)
	(on b2 b16)
	(on b16 b1)
	(on b1 b17)
	(on b17 b10)
	(ontable b10)
	(on b0 b15)
	(on b15 b4)
	(ontable b4)))
)
