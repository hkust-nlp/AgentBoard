;; See problem file for a description of what this is about.

(define (domain GROUNDED-TRUCKS)

(:requirements
:strips
)

(:predicates
(at-destination_package1_l1)
(at-destination_package1_l2)
(at_package1_l1)
(at_package1_l2)
(at_truck1_l1)
(at_truck1_l2)
(delivered_package1_l1_t1)
(delivered_package1_l1_t2)
(delivered_package1_l2_t1)
(delivered_package1_l2_t2)
(free_a1_truck1)
(in_package1_truck1_a1)
(time-now_t0)
(time-now_t1)
(time-now_t2)
)

(:action LOAD_PACKAGE1_TRUCK1_A1_L1
:parameters ()
:precondition
(and
(at_truck1_l1)
(at_package1_l1)
(free_a1_truck1)
)
:effect
(and
(in_package1_truck1_a1)
(not (free_a1_truck1))
(not (at_package1_l1))
)
)

(:action LOAD_PACKAGE1_TRUCK1_A1_L2
:parameters ()
:precondition
(and
(at_truck1_l2)
(at_package1_l2)
(free_a1_truck1)
)
:effect
(and
(in_package1_truck1_a1)
(not (free_a1_truck1))
(not (at_package1_l2))
)
)

(:action UNLOAD_PACKAGE1_TRUCK1_A1_L1
:parameters ()
:precondition
(and
(at_truck1_l1)
(in_package1_truck1_a1)
)
:effect
(and
(at_package1_l1)
(free_a1_truck1)
(not (in_package1_truck1_a1))
)
)

(:action UNLOAD_PACKAGE1_TRUCK1_A1_L2
:parameters ()
:precondition
(and
(at_truck1_l2)
(in_package1_truck1_a1)
)
:effect
(and
(at_package1_l2)
(free_a1_truck1)
(not (in_package1_truck1_a1))
)
)

(:action DELIVER_PACKAGE1_L1_T1_T1
:parameters ()
:precondition
(and
(time-now_t1)
(at_package1_l1)
)
:effect
(and
(delivered_package1_l1_t1)
(at-destination_package1_l1)
(not (at_package1_l1))
)
)

(:action DELIVER_PACKAGE1_L1_T1_T2
:parameters ()
:precondition
(and
(time-now_t1)
(at_package1_l1)
)
:effect
(and
(delivered_package1_l1_t2)
(at-destination_package1_l1)
(not (at_package1_l1))
)
)

(:action DELIVER_PACKAGE1_L1_T2_T2
:parameters ()
:precondition
(and
(time-now_t2)
(at_package1_l1)
)
:effect
(and
(delivered_package1_l1_t2)
(at-destination_package1_l1)
(not (at_package1_l1))
)
)

(:action DELIVER_PACKAGE1_L2_T1_T1
:parameters ()
:precondition
(and
(time-now_t1)
(at_package1_l2)
)
:effect
(and
(delivered_package1_l2_t1)
(at-destination_package1_l2)
(not (at_package1_l2))
)
)

(:action DELIVER_PACKAGE1_L2_T1_T2
:parameters ()
:precondition
(and
(time-now_t1)
(at_package1_l2)
)
:effect
(and
(delivered_package1_l2_t2)
(at-destination_package1_l2)
(not (at_package1_l2))
)
)

(:action DELIVER_PACKAGE1_L2_T2_T2
:parameters ()
:precondition
(and
(time-now_t2)
(at_package1_l2)
)
:effect
(and
(delivered_package1_l2_t2)
(at-destination_package1_l2)
(not (at_package1_l2))
)
)

(:action DRIVE_TRUCK1_L1_L2_T0_T1
:parameters ()
:precondition
(and
(time-now_t0)
(at_truck1_l1)
)
:effect
(and
(time-now_t1)
(at_truck1_l2)
(not (at_truck1_l1))
(not (time-now_t0))
)
)

(:action DRIVE_TRUCK1_L1_L2_T1_T2
:parameters ()
:precondition
(and
(time-now_t1)
(at_truck1_l1)
)
:effect
(and
(time-now_t2)
(at_truck1_l2)
(not (at_truck1_l1))
(not (time-now_t1))
)
)

(:action DRIVE_TRUCK1_L2_L1_T0_T1
:parameters ()
:precondition
(and
(time-now_t0)
(at_truck1_l2)
)
:effect
(and
(time-now_t1)
(at_truck1_l1)
(not (at_truck1_l2))
(not (time-now_t0))
)
)

(:action DRIVE_TRUCK1_L2_L1_T1_T2
:parameters ()
:precondition
(and
(time-now_t1)
(at_truck1_l2)
)
:effect
(and
(time-now_t2)
(at_truck1_l1)
(not (at_truck1_l2))
(not (time-now_t1))
)
)

)
