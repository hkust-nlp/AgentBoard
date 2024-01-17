(define (domain footwear)
    (:requirements :strips :typing)
    (:types sock shoe foot place)
    (:predicates 
        (isblue ?sock - sock)
        (isred ?sock - sock)
        (isstriped ?sock - sock)
        (isplain ?sock - sock)
        (socksmatch ?sock1 - sock ?sock2 - sock)
        (sockfree ?sock - sock)
        
        (isdressshoe ?shoe - shoe)
        (issneaker ?shoe - shoe)
        (isboot ?shoe - shoe)
        (issandle ?shoe - shoe)
        (shoefree ?shoe - shoe)

        (isbare ?foot - foot)
        (hassock ?foot - foot)
        (hasshoe ?foot - foot)
        (wearingsock ?sock - sock)
        (wearingshoe ?shoe - shoe)
        (sockon ?sock - sock ?foot - foot)
        (shoeon ?shoe - shoe ?foot - foot)
        (shoeseq ?shoe1 - shoe ?shoe2 - shoe)

        (home ?place - place)
        (office ?place - place)
        (gym ?place - place)
        (forest ?place - place)
        (beach ?place - place)
        (at ?place - place)

        (presentationdoneat ?place - place)
        (workedoutat ?place - place)
        (hikedat ?place - place)
        (swamat ?place - place)
    )

    (:action puton-sock
        :parameters (?foot - foot ?sock - sock ?place - place)
        :precondition (and
            (at ?place) 
            (home ?place)
            (isbare ?foot)
            (sockfree ?sock)
        )
        :effect (and
            (not (isbare ?foot))
            (not (sockfree ?sock))
            (hassock ?foot)
            (wearingsock ?sock)
            (sockon ?sock ?foot)
        )
    )

    (:action remove-sock
        :parameters (?foot - foot ?sock - sock ?place - place)
        :precondition (and
            (at ?place)
            (home ?place)
            (sockon ?sock ?foot)
        )
        :effect (and
            (isbare ?foot)
            (sockfree ?sock)
            (not (hassock ?foot))
            (not (wearingsock ?sock))
            (not (sockon ?sock ?foot))
        )
    )

    (:action puton-shoe
        :parameters (?foot - foot ?shoe - shoe ?place - place)
        :precondition (and
            (at ?place) 
            (home ?place)
            (hassock ?foot)
            (shoefree ?shoe)
        )
        :effect (and
            (not (hassock ?foot))
            (not (shoefree ?shoe))
            (hasshoe ?foot)
            (wearingshoe ?shoe)
            (shoeon ?shoe ?foot)
        )
    )

    (:action remove-shoe
        :parameters (?foot - foot ?sock - sock ?shoe - shoe ?place - place)
        :precondition (and
            (at ?place)
            (home ?place)
            (sockon ?sock ?foot)
            (shoeon ?shoe ?foot)
        )
        :effect (and
            (not (hasshoe ?foot))
            (not (wearingshoe ?shoe))
            (not (shoeon ?shoe ?foot))
            (hassock ?foot)
            (wearingsock ?sock)
            (sockon ?sock ?foot)
            (shoefree ?shoe)
        )
    )

    (:action goto-home
        :parameters (?from - place ?to - place)
        :precondition (and
            (at ?from) 
            (home ?to)
        )
        :effect (and
            (not (at ?from))
            (at ?to)
        )
    )

    (:action goto-office
        :parameters (?from - place ?to - place ?s1 - sock ?s2 - sock ?sh1 - shoe ?sh2 - shoe)
        :precondition (and
            (at ?from) 
            (office ?to)
            (socksmatch ?s1 ?s2)
            (wearingsock ?s1)
            (wearingsock ?s2)
            (isdressshoe ?sh1)
            (isdressshoe ?sh2)
            (wearingshoe ?sh1)
            (wearingshoe ?sh2)
            (not (shoeseq ?sh1 ?sh2))
        )
        :effect (and
            (not (at ?from))
            (at ?to)
            (presentationdoneat ?to)
        )
    )

    (:action goto-gym
        :parameters (?from - place ?to - place ?sh1 - shoe ?sh2 - shoe)
        :precondition (and
            (at ?from) 
            (gym ?to)
            (issneaker ?sh1)
            (issneaker ?sh2)
            (wearingshoe ?sh1)
            (wearingshoe ?sh2)
            (not (shoeseq ?sh1 ?sh2))
        )
        :effect (and
            (not (at ?from))
            (at ?to)
            (workedoutat ?to)
        )
    )

    (:action goto-forest
        :parameters (?from - place ?to - place ?sh1 - shoe ?sh2 - shoe)
        :precondition (and
            (at ?from) 
            (forest ?to)
            (isboot ?sh1)
            (isboot ?sh2)
            (wearingshoe ?sh1)
            (wearingshoe ?sh2)
            (not (shoeseq ?sh1 ?sh2))
        )
        :effect (and
            (not (at ?from))
            (at ?to)
            (hikedat ?to)
        )
    )

    (:action goto-beach
        :parameters (?from - place ?to - place ?sh1 - shoe ?sh2 - shoe)
        :precondition (and
            (at ?from) 
            (beach ?to)
            (issandle ?sh1)
            (issandle ?sh2)
            (wearingshoe ?sh1)
            (wearingshoe ?sh2)
            (not (shoeseq ?sh1 ?sh2))
        )
        :effect (and
            (not (at ?from))
            (at ?to)
            (swamat ?to)
        )
    )
)
