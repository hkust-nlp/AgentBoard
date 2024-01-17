(define (problem baking) 
    (:domain baking)

    (:objects
      oven-0 - oven
      oven-1 - oven
      egg-0 - ingredient
      egg-1 - ingredient
      flour-0 - ingredient
      pan-0 - pan
      pan-1 - pan
      new-0 - ingredient
      new-1 - ingredient
      soap-0 - soap
    )

    (:init
    
    (isegg egg-0)
    (isegg egg-1)
    (isflour flour-0)
    (hypothetical new-0)
    (hypothetical new-1)
    (panisclean pan-0)
    (panisclean pan-1)
    (soapconsumed soap-0)

    ; action literals
    (putegginpan egg-0 pan-0)
    (putegginpan egg-1 pan-0)
    (putflourinpan flour-0 pan-0)
    (mix pan-0)
    (putpaninoven pan-0 oven-0)
    (putpaninoven pan-0 oven-1)
    (removepanfromoven pan-0)
    (cleanpan pan-0 soap-0)
    (putegginpan egg-0 pan-1)
    (putegginpan egg-1 pan-1)
    (putflourinpan flour-0 pan-1)
    (mix pan-1)
    (putpaninoven pan-1 oven-0)
    (putpaninoven pan-1 oven-1)
    (removepanfromoven pan-1)
    (cleanpan pan-1 soap-0)
    (bakecake new-0 oven-0)
    (bakecake new-1 oven-0)
    (bakesouffle new-0 oven-0)
    (bakesouffle new-1 oven-0)
    (bakecake new-0 oven-1)
    (bakecake new-1 oven-1)
    (bakesouffle new-0 oven-1)
    (bakesouffle new-1 oven-1)
    )

    (:goal (and 
        (issouffle new-0) 
        (iscake new-1) 
        (not (ovenisfull oven-0))
        (not (ovenisfull oven-1))
    ))
)
    