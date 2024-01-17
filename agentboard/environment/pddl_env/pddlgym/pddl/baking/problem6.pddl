(define (problem baking) 
    (:domain baking)

    (:objects
      oven-0 - oven
      egg-0 - ingredient
      egg-1 - ingredient
      flour-0 - ingredient
      flour-1 - ingredient
      pan-0 - pan
      new-0 - ingredient
      new-1 - ingredient
      soap-0 - soap
    )

    (:init
    
    (isegg egg-0)
    (isegg egg-1)
    (isflour flour-0)
    (isflour flour-1)
    (hypothetical new-0)
    (hypothetical new-1)
    (panisclean pan-0)

    ; action literals
    (putegginpan egg-0 pan-0)
    (putegginpan egg-1 pan-0)
    (putflourinpan flour-0 pan-0)
    (putflourinpan flour-1 pan-0)
    (mix pan-0)
    (putpaninoven pan-0 oven-0)
    (removepanfromoven pan-0)
    (cleanpan pan-0 soap-0)
    (bakecake new-0 oven-0)
    (bakecake new-1 oven-0)
    (bakesouffle new-0 oven-0)
    (bakesouffle new-1 oven-0)
    )

    (:goal (and 
        (iscake new-0) 
        (iscake new-1) 
    ))
)
    