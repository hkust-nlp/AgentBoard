
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
	b21 - block
	b22 - block
	b23 - block
	b24 - block
	b25 - block
	b26 - block
	b27 - block
	b28 - block
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
	(clear b20)
	(clear b24)
	(clear b5)
	(handempty)
	(on b0 b1)
	(on b10 b11)
	(on b11 b12)
	(on b12 b13)
	(on b13 b14)
	(on b15 b16)
	(on b16 b17)
	(on b17 b18)
	(on b18 b19)
	(on b1 b2)
	(on b20 b21)
	(on b21 b22)
	(on b22 b23)
	(on b24 b25)
	(on b25 b26)
	(on b26 b27)
	(on b27 b28)
	(on b2 b3)
	(on b3 b4)
	(on b5 b6)
	(on b6 b7)
	(on b7 b8)
	(on b8 b9)
	(ontable b14)
	(ontable b19)
	(ontable b23)
	(ontable b28)
	(ontable b4)
	(ontable b9)
  )
  (:goal (and
	(on b26 b13)
	(on b13 b27)
	(on b27 b14)
	(on b14 b11)
	(ontable b11)
	(on b20 b3)
	(on b3 b16)
	(on b16 b7)
	(on b7 b25)
	(ontable b25)
	(on b0 b6)
	(on b6 b4)
	(on b4 b15)
	(ontable b15)
	(on b8 b18)
	(on b18 b23)
	(on b23 b12)
	(ontable b12)))
)
