(define (problem baking) 
    (:domain baking)

    (:objects
      oven-0 - oven
      egg-0 - ingredient
      flour-0 - ingredient
      soap-0 - soap
      pan-0 - pan
      new-0 - ingredient
    )

    (:init
    
    (isegg egg-0)
    (isflour flour-0)
    (hypothetical new-0)

    ; action literals
    (putegginpan egg-0 pan-0)
    (putflourinpan flour-0 pan-0)
    (mix pan-0)
    (putpaninoven pan-0 oven-0)
    (removepanfromoven pan-0)
    (bakecake new-0 oven-0)
    (bakesouffle new-0 oven-0)
    (cleanpan pan-0 soap-0)

    )

    (:goal (and (issouffle new-0) ))
)
    