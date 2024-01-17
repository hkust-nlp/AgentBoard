(define (problem BW-rand-50)
(:domain blocksworld)
(:objects b1 b2 b3 - block)
(:init
(handempty)
(on b1 b2)
(on b2 b3)
(ontable b3)
(clear b1)
)
(:goal
(and
(on b1 b2)
(on b1 b3)
)
)
)


