;; Problem to test issue75. If we add the implied preconditions, the
;; preprocessor cannot prune any variables; if we do, it can prune lots.
;;
;; Pruning the variables is safe and should be done: the variables
;; that are pruned are ones that are only set by effects, but not
;; mentioned in the goal or used as preconditions. (Adding the implied
;; preconditions causes them to be mentioned in the preconditions,
;; which means that relevance analysis can't detect them as useless
;; any more.)
;;
;; This is based on Trucks-Strips #1, with the following modifications:
;;
;; - Removed everything pertaining to packages 2 and 3.
;; - Removed atom (foo).
;; - Changed goal deadline from t3 to t2.
;; - Removed storage space (if that's what it is) a2.
;; - Removed everything pertaining to timesteps t3, t4, t5 and t6.
;; - Changed truck init location and package goal location to l2.
;; - Removed everything pertaining to location l3.

(define (problem GROUNDED-TRUCK-1)
(:domain GROUNDED-TRUCKS)
(:init
(at_package1_l2)
(at_truck1_l1)
(free_a1_truck1)
(time-now_t0)
)
(:goal
(and
(delivered_package1_l1_t2)
)
)
)
