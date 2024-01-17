; this is a comment
(define (problem test-problem)
  (:domain test-domain)
  (:objects
    nomsy - jindo
    rover - corgi
    rene - cat
    block1 - block
    block2 - block
    cylinder1 - cylinder
  )

  (:init
    (ispresent nomsy)
    (ispresent rover)
    (ispresent rene)
    (ispresent block1)
    (ispresent block2)
    (ispresent cylinder1)
    (islight block1)
    (islight cylinder1)
    (isfurry nomsy)
  )

  (:goal (and
    (attending nomsy cylinder1)
  ))
)
s