(define (problem blocks)
    (:domain blocks)
    (:objects 
        d - block
        b - block
        a - block
        c - block
        robot - robot
    )
    (:init 
        (clear c) 
        (clear a) 
        (clear b) 
        (clear d) 
        (ontable c) 
        (ontable a)
        (ontable b) 
        (ontable d) 
        (handempty robot)

        ; action literals
        (pickup a)
        (putdown a)
        (unstack a)
        (stack a b)
        (stack a c)
        (stack a d)
        (pickup b)
        (putdown b)
        (unstack b)
        (stack b a)
        (stack b c)
        (stack b d)
        (pickup c)
        (putdown c)
        (unstack c)
        (stack c b)
        (stack c a)
        (stack c d)
        (pickup d)
        (putdown d)
        (unstack d)
        (stack d b)
        (stack d c)
        (stack d a)

    )
    (:goal (and (on d c) (on c b) (on b a)))
)
