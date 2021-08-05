# Documentation on the Meteocode fields

Most fields start with `start` and `end` which are given in number of hour since the issue time of the report.
Historical data (i.e start and end times before issue time) is indicated with a negative number

## Precipitation accumulation
`accum`: `[start end type code certainty value-start value-end?]`

* `code` :
* `certainty` :


## cloud cover
`ciel`: `[start end neb-start neb-end {ceiling-height}]`  

* `neb-start`,`neb-end` : cloud cover in tenths of cloud-cover at start and end time
* `ceiling-height` : 1-10: 0->20000 ft

