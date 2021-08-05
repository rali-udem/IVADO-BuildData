# Documentation on the Meteocode fields
Information taken from *Météocode Coding standard Version 3.9.1* (Meteocode38.doc)
We only give frequently occurring values, refer to the document for not documented values. The original being in French, we give equivalent English terms after `=>`.

Most fields start with `start` and `end` which are given in number of hour since the issue time of the report.
Historical data (i.e start and end times before issue time) is indicated with a negative number

## Precipitation accumulation (sect 3.4.4, p. 22)
    accum: start end type code certainty value-start value-end?
        code : "additionnelle" | "partielle" | "totale" =>
               "additionnal" | "partial" | "total"
        certainty : "moins_de" | "plus_de" | "possible" | "pouvant_atteindre" | "pouvant_depasser" | "pres_de" =>
                    "less than" | "more than" | "possible" | "possibly reaching" | "possibly exceeding" | "near"


## Cloud cover (sect 3.4.6, p. 28)
    ciel: start end neb-start neb-end {ceiling-height}
        neb-start,neb-end : cloud cover in tenths of cloud-cover at start and end time
        ceiling-height` : 1..10 (1 being low and 10 high)

## Climatological data for temperature (sect 3.4.9, p 31)
    climat_temp : start end type value
        type : "max" | "min" | "moy" =>
               "max" | "min" | "average"
        value : degree in Celsius

## Air quality index (sect 3.4.14, p 35)
    indice_qa : start end value
        value : 0..100 (float)

## UV index (sect 3.4.16, p 36)
    indice_uv : start end value
        value : float with one decimal

## Snow level (???)
    niveau_neige : start end code number

## Precipitations (sect 3.4.18, p 37)
    pcpn : start end certainty code type intensity frequency exception?
        certainty : "certain" | "possible" | "risque" =>
                    "certain" | "possible" | "risk"
        code : "debut" | "debut_fin" | "exact" | "fin" =>
               "start" | "start_end" | "exact" | "end"
        type : "averses" | "averses_neige" | "averses_neige_fondante" | "blizzard" | 
               "bourrasques_neige" | "bruine" | "bruine_verglacante" | 
               "cristaux_glace" |"grele"| "gresil" | "neige" | "neige_fondante" | 
               "orages" | "pluie" | "pluie_verglacante" | "poudrerie" 
               =>
               "showers" | "flurries" | "wet flurries" | "blizzard" | 
               "snow squalls" | "drizzle" | "freezing drizzle" | 
               "ice crystals" |"hail"| "ice pellets" | "snow" | "wet snow" | 
               "thunderstorm" | "rain" | "freezing rain" | "blowing snow"
        intensity : "faible" | "fort" | "modere" | "nil" | "tres_faible" =>
                    "light" | "heavy" | "moderate" | *implicit* | "very light"
        frequency : "bref" | "continuel" | "frequent" | "occasionnel" | "peu" =>
                    "brief" | "continual" | "frequent" | "occasionnal" | "few"
        exception : embedded list of pcpn

## Precipitation probability (sect 3.4.20, p 41)
    prob : "seuil" value []+

        