
(define (problem trapnewspaper) (:domain trapnewspapers)
  (:objects
        loc-0 - loc
    loc-1 - loc
    loc-2 - loc
    loc-3 - loc
    paper-0 - paper
    paper-1 - paper
    paper-2 - paper
    paper-3 - paper
    paper-4 - paper
    paper-5 - paper
    paper-6 - paper
  )
  (:init 
    (at loc-0)
    (ishomebase loc-0)
    (safe loc-0)
    (safe loc-2)
    (unpacked paper-0)
    (unpacked paper-1)
    (unpacked paper-2)
    (unpacked paper-3)
    (unpacked paper-4)
    (unpacked paper-5)
    (unpacked paper-6)
    (wantspaper loc-2)
  )
  (:goal (and
    (satisfied loc-2)))
)
