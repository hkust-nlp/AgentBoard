(define (domain hanoi)
  (:requirements :strips)
  (:predicates
  (clear ?x)
  (on ?x ?y)
  (smaller ?x ?y)
  (move ?disc ?to)
  )

  ; (:actions move)

  (:action move
    :parameters (?disc ?from ?to)
    :precondition (and (move ?disc ?to) (smaller ?to ?disc) (on ?disc ?from)
               (clear ?disc) (clear ?to))
    :effect  (and (clear ?from) (on ?disc ?to) (not (on ?disc ?from))
          (not (clear ?to))))
  )
