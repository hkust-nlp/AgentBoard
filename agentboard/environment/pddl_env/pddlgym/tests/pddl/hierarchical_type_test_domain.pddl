; this is a comment
(define (domain test-domain)
  (:requirements :typing )
  (:types dog cat - animal
          block cylinder - object
          jindo corgi - dog
          animal object - entity
  )
  (:predicates (isfurry ?x - animal)
               (ishappy ?x - animal)
               (islight ?x - object)
               (attending ?x - animal ?y - object)
               (pet ?x - animal)
               (throw ?x - object)
               (ispresent ?x - entity)
  )

  ; (:actions pet throw)

  (:action pet
   :parameters (?x - animal)
   :precondition (and (pet ?x)
                      (isfurry ?x)
                 )
   :effect       (and (ishappy ?x)
                 )
   )

  (:action throw
   :parameters (?x - object ?y - animal)
   :precondition (and (throw ?x)
                      (islight ?x)
                      (ishappy ?y)
                 )
   :effect       (and (attending ?x ?y)
                 )
   )
)