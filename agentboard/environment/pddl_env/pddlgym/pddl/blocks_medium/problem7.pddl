
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
	(clear b13)
	(clear b17)
	(clear b5)
	(clear b8)
	(handempty)
	(on b0 b1)
	(on b10 b11)
	(on b11 b12)
	(on b13 b14)
	(on b14 b15)
	(on b15 b16)
	(on b17 b18)
	(on b18 b19)
	(on b19 b20)
	(on b1 b2)
	(on b2 b3)
	(on b3 b4)
	(on b5 b6)
	(on b6 b7)
	(on b8 b9)
	(on b9 b10)
	(ontable b12)
	(ontable b16)
	(ontable b20)
	(ontable b4)
	(ontable b7)
  )
  (:goal (and
	(on b2 b3)
	(on b3 b17)
	(on b17 b15)
	(ontable b15)
	(on b8 b5)
	(on b5 b10)
	(on b10 b13)
	(on b13 b12)
	(ontable b12)
	(on b14 b7)
	(on b7 b6)
	(on b6 b1)
	(on b1 b18)
	(ontable b18)
	(on b0 b16)
	(on b16 b19)
	(on b19 b4)
	(ontable b4)
	(on b11 b9)
	(on b9 b20)
	(ontable b20)))
)
