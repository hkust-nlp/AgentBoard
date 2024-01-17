;; Small test domain for the problem of issue49.

(define (domain issue49)
  (:predicates
   (A)
   (B)
   (C)
   )

  (:action action-a
           :precondition (A)
           :effect (B)
           )
)
