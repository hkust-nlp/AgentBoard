
(define (problem trapnewspaper) (:domain trapnewspapers)
  (:objects
        loc-0 - loc
	loc-1 - loc
	loc-10 - loc
	loc-11 - loc
	loc-2 - loc
	loc-3 - loc
	loc-4 - loc
	loc-5 - loc
	loc-6 - loc
	loc-7 - loc
	loc-8 - loc
	loc-9 - loc
	paper-0 - paper
	paper-1 - paper
	paper-10 - paper
	paper-11 - paper
	paper-12 - paper
	paper-13 - paper
	paper-14 - paper
	paper-15 - paper
	paper-2 - paper
	paper-3 - paper
	paper-4 - paper
	paper-5 - paper
	paper-6 - paper
	paper-7 - paper
	paper-8 - paper
	paper-9 - paper
  )
  (:init 
	(at loc-0)
	(ishomebase loc-0)
	(safe loc-0)
	(safe loc-10)
	(safe loc-11)
	(safe loc-1)
	(safe loc-3)
	(safe loc-5)
	(safe loc-6)
	(safe loc-7)
	(safe loc-9)
	(unpacked paper-0)
	(unpacked paper-10)
	(unpacked paper-11)
	(unpacked paper-12)
	(unpacked paper-13)
	(unpacked paper-14)
	(unpacked paper-15)
	(unpacked paper-1)
	(unpacked paper-2)
	(unpacked paper-3)
	(unpacked paper-4)
	(unpacked paper-5)
	(unpacked paper-6)
	(unpacked paper-7)
	(unpacked paper-8)
	(unpacked paper-9)
	(wantspaper loc-10)
	(wantspaper loc-11)
	(wantspaper loc-1)
	(wantspaper loc-3)
	(wantspaper loc-5)
	(wantspaper loc-6)
	(wantspaper loc-7)
	(wantspaper loc-9)
  )
  (:goal (and
	(satisfied loc-1)
	(satisfied loc-3)
	(satisfied loc-5)
	(satisfied loc-6)
	(satisfied loc-7)
	(satisfied loc-9)
	(satisfied loc-10)
	(satisfied loc-11)))
)
