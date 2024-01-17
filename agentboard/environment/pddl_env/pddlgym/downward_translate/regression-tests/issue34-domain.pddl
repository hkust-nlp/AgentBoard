;; PipesWorld

(define (domain pipesworld_strips)

(:requirements :strips :typing )

;; Types
;;  pipe: a pipeline segment
;;  area: operational areas
;;  product: an oil derivative product, such as gasoline,
;;    kerosene, etc.
;;  batch-atom: an unitary batch

(:types pipe area product batch-atom )

;; Define the products (petroleum derivatives)
(:constants lco gasoleo rat-a oca1 oc1b - product )
(:predicates

  ;; Indicates that a pipeline segment connects
  ;; two areas
  (connect ?from ?to - area ?pipe - pipe)

  ;; Special case for unitary pipes
  (unitary ?pipe - pipe)
  (not-unitary ?pipe - pipe)

  ;; These predicates represent the pipeline segment contents
  ;; We define the first (nearest to  ``from'' area) and 
  ;; last (nearest to  ``to'' area) batch-atom in a pipeline 
  ;; segment, and their sequence is represented by the
  ;; (follow) predicate
  (last ?batch-atom - batch-atom ?pipe - pipe)
  (first ?batch-atom - batch-atom ?pipe - pipe)
  (follow ?next ?previous - batch-atom)

  ;; An unitary batch product
  (is-product ?batch-atom - batch-atom ?product - product)

  ;; Unitary batches that are on areas
  (on ?batch-atom - batch-atom ?area - area)

  ;; Indicates that two products may interface in the
  ;; pipeline segment
  (may-interface ?product-a ?product-b - product)

  ;; to control splitting process (push/pop vs. update)
  (normal ?pipe - pipe)
  (push-updating ?pipe - pipe)
  (pop-updating ?pipe - pipe)
)

;; PUSH-START action
;; Moves a batch-atom from a tankage to a pipeline segment
;; The PUSH-START action moves the pipeline segment contents towards
;; the ``to-area'' defined in the ``connect'' predicate
;; first part -- initialise the push and turn control
;; over to contents update operators

(:action PUSH-START
  :parameters(
    ;; Pipeline segment that will be moved
    ?pipe - pipe
    ;; Unitary batch that will be inserted into the pipeline
    ;; segment
    ?batch-atom-in - batch-atom
    ?from-area - area
    ?to-area - area
    ?first-batch-atom - batch-atom
    ?product-batch-atom-in - product
    ?product-first-batch - product
  )
  :precondition
   (and

   ;; normal planning mode
   (normal ?pipe)
   ;; Binds :vars section
   (first ?first-batch-atom ?pipe)
   (connect ?from-area ?to-area ?pipe)
   ;; Inserted batch must be in 'from-area'
   (on ?batch-atom-in ?from-area)
   ;; Action is applicable only in non-unitary pipeline segments
   (not-unitary ?pipe)
   ;; Bind batch-atom products
   (is-product ?batch-atom-in ?product-batch-atom-in)
   (is-product ?first-batch-atom ?product-first-batch)
   ;; Interface restriction
   (may-interface ?product-batch-atom-in ?product-first-batch)

 )
  :effect
   (and 
     ;; switch into correct update mode for this pipe
     (push-updating ?pipe)
     (not (normal ?pipe))
     ;; The inserted unitary batch will be the pipeline segment
     ;; new first batch
     (first ?batch-atom-in ?pipe)
     (not (first ?first-batch-atom ?pipe))

     ;; Updates the follow and last relationship to the new
     ;; pipeline segment configuration
     (follow ?first-batch-atom ?batch-atom-in)
     ;; Inserted batch-atom is removed from area
     (not (on ?batch-atom-in ?from-area))
    ;; Batch-atom removed from pipeline segment is inserted
    ;; into the destination area
)
)
;; PUSH-END action
;; Moves a batch-atom from a tankage to a pipeline segment
;; The PUSH-END action moves the pipeline segment contents towards
;; the ``to-area'' defined in the ``connect'' predicate
;; second part -- when start of pipe has been done, care about the
;; end of the pipe

(:action PUSH-END
  :parameters(
    ;; Pipeline segment that will be moved
    ?pipe - pipe
    ;; Unitary batch that will be inserted into the pipeline
    ;; segment
    ?from-area - area
    ?to-area - area
    ?last-batch-atom - batch-atom
    ?next-last-batch-atom - batch-atom
  )
  :precondition
   (and

   ;; are we in the correct mode?
   (push-updating ?pipe)
   ;; Binds :vars section
   (last ?last-batch-atom ?pipe)
   (connect ?from-area ?to-area ?pipe)
   ;; Action is applicable only in non-unitary pipeline segments
   (not-unitary ?pipe)
   (follow ?last-batch-atom ?next-last-batch-atom)

 )
  :effect
   (and 
     ;; back to normal mode
     (not (push-updating ?pipe))
     (normal ?pipe)

     ;; Updates the follow and last relationship to the new
     ;; pipeline segment configuration
     (not (follow ?last-batch-atom ?next-last-batch-atom))
     (last ?next-last-batch-atom ?pipe)
     ;; Previous last batch is not last anymore
     (not (last ?last-batch-atom ?pipe))
    ;; Batch-atom removed from pipeline segment is inserted
    ;; into the destination area
     (on ?last-batch-atom ?to-area)
)
)
;; POP-START action
;; Moves a batch-atom from a tankage to a pipeline segment
;; The POP-START action moves the pipeline segment contents towards
;; the ``from-area'' defined in the ``connect'' predicate
;; first part -- initialise the pop and turn control
;; over to contents update operators

(:action POP-START
  :parameters(
    ;; Pipeline segment that will be moved
    ?pipe - pipe
    ;; Unitary batch that will be inserted into the pipeline
    ;; segment
    ?batch-atom-in - batch-atom
    ?from-area - area
    ?to-area - area
    ?last-batch-atom - batch-atom
    ?product-batch-atom-in - product
    ?product-last-batch - product
  )
  :precondition
   (and

   ;; normal planning mode
   (normal ?pipe)
   ;; Binds :vars section
   (last ?last-batch-atom ?pipe)
   (connect ?from-area ?to-area ?pipe)
   ;; Inserted batch must be in 'to-area'
   (on ?batch-atom-in ?to-area)
   ;; Action is applicable only in non-unitary pipeline segments
   (not-unitary ?pipe)
   ;; Bind batch-atom products
   (is-product ?batch-atom-in ?product-batch-atom-in)
   (is-product ?last-batch-atom ?product-last-batch)
   ;; Interface restriction
   (may-interface ?product-batch-atom-in ?product-last-batch)

 )
  :effect
   (and 
     ;; switch into correct update mode for this pipe
     (pop-updating ?pipe)
     (not (normal ?pipe))
     ;; The inserted unitary batch will be the pipeline segment
     ;; new last batch
     (last ?batch-atom-in ?pipe)
     (not (last ?last-batch-atom ?pipe))

     ;; Updates the follow and first relationship to the new
     ;; pipeline segment configuration
     (follow ?batch-atom-in ?last-batch-atom)
     ;; Inserted batch-atom is removed from area
     (not (on ?batch-atom-in ?to-area))
    ;; Batch-atom removed from pipeline segment is inserted
    ;; into the destination area
)
)
;; POP-END action
;; Moves a batch-atom from a tankage to a pipeline segment
;; The POP-END action moves the pipeline segment contents towards
;; the ``from-area'' defined in the ``connect'' predicate
;; second part -- when start of pipe has been done, care about the
;; end of the pipe

(:action POP-END
  :parameters(
    ;; Pipeline segment that will be moved
    ?pipe - pipe
    ;; Unitary batch that will be inserted into the pipeline
    ;; segment
    ?from-area - area
    ?to-area - area
    ?first-batch-atom - batch-atom
    ?next-first-batch-atom - batch-atom
  )
  :precondition
   (and

   ;; are we in the correct mode?
   (pop-updating ?pipe)
   ;; Binds :vars section
   (first ?first-batch-atom ?pipe)
   (connect ?from-area ?to-area ?pipe)
   ;; Action is applicable only in non-unitary pipeline segments
   (not-unitary ?pipe)
   (follow ?next-first-batch-atom ?first-batch-atom)

 )
  :effect
   (and 
     ;; back to normal mode
     (not (pop-updating ?pipe))
     (normal ?pipe)

     ;; Updates the follow and first relationship to the new
     ;; pipeline segment configuration
     (not (follow ?next-first-batch-atom ?first-batch-atom))
     (first ?next-first-batch-atom ?pipe)
     ;; Previous first batch is not first anymore
     (not (first ?first-batch-atom ?pipe))
    ;; Batch-atom removed from pipeline segment is inserted
    ;; into the destination area
     (on ?first-batch-atom ?from-area)
)
)
;; PUSH-UNITARYPIPE action
;; Moves a batch-atom from a tankage to a pipeline segment
;; The PUSH-UNITARYPIPE action moves the pipeline segment contents towards
;; the ``to-area'' defined in the ``connect'' predicate
;; first part -- initialise the push and turn control
;; over to contents update operators

(:action PUSH-UNITARYPIPE
  :parameters(
    ;; Pipeline segment that will be moved
    ?pipe - pipe
    ;; Unitary batch that will be inserted into the pipeline
    ;; segment
    ?batch-atom-in - batch-atom
    ?from-area - area
    ?to-area - area
    ?first-batch-atom - batch-atom
    ?product-batch-atom-in - product
    ?product-first-batch - product
  )
  :precondition
   (and

   ;; Binds :vars section
   (first ?first-batch-atom ?pipe)
   (connect ?from-area ?to-area ?pipe)
   ;; Inserted batch must be in 'from-area'
   (on ?batch-atom-in ?from-area)
   ;; Action is applicable only in unitary pipeline segments
   (unitary ?pipe)
   ;; Bind batch-atom products
   (is-product ?batch-atom-in ?product-batch-atom-in)
   (is-product ?first-batch-atom ?product-first-batch)
   ;; Interface restriction
   (may-interface ?product-batch-atom-in ?product-first-batch)

 )
  :effect
   (and 
     ;; The inserted unitary batch will be the pipeline segment
     ;; new first batch
     (first ?batch-atom-in ?pipe)
     (not (first ?first-batch-atom ?pipe))

     ;; Updates the follow and last relationship to the new
     ;; pipeline segment configuration
     (last ?batch-atom-in ?pipe)
     (not (last ?first-batch-atom ?pipe))
     ;; Inserted batch-atom is removed from area
     (not (on ?batch-atom-in ?from-area))
    ;; Batch-atom removed from pipeline segment is inserted
    ;; into the destination area
     (on ?first-batch-atom ?to-area)
)
)
;; POP-UNITARYPIPE action
;; Moves a batch-atom from a tankage to a pipeline segment
;; The POP-UNITARYPIPE action moves the pipeline segment contents towards
;; the ``from-area'' defined in the ``connect'' predicate
;; first part -- initialise the pop and turn control
;; over to contents update operators

(:action POP-UNITARYPIPE
  :parameters(
    ;; Pipeline segment that will be moved
    ?pipe - pipe
    ;; Unitary batch that will be inserted into the pipeline
    ;; segment
    ?batch-atom-in - batch-atom
    ?from-area - area
    ?to-area - area
    ?last-batch-atom - batch-atom
    ?product-batch-atom-in - product
    ?product-last-batch - product
  )
  :precondition
   (and

   ;; Binds :vars section
   (last ?last-batch-atom ?pipe)
   (connect ?from-area ?to-area ?pipe)
   ;; Inserted batch must be in 'to-area'
   (on ?batch-atom-in ?to-area)
   ;; Action is applicable only in unitary pipeline segments
   (unitary ?pipe)
   ;; Bind batch-atom products
   (is-product ?batch-atom-in ?product-batch-atom-in)
   (is-product ?last-batch-atom ?product-last-batch)
   ;; Interface restriction
   (may-interface ?product-batch-atom-in ?product-last-batch)

 )
  :effect
   (and 
     ;; The inserted unitary batch will be the pipeline segment
     ;; new last batch
     (last ?batch-atom-in ?pipe)
     (not (last ?last-batch-atom ?pipe))

     ;; Updates the follow and first relationship to the new
     ;; pipeline segment configuration
     (first ?batch-atom-in ?pipe)
     (not (first ?last-batch-atom ?pipe))
     ;; Inserted batch-atom is removed from area
     (not (on ?batch-atom-in ?to-area))
    ;; Batch-atom removed from pipeline segment is inserted
    ;; into the destination area
     (on ?last-batch-atom ?from-area)
)
)
)
