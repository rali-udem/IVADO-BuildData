# Create JSON data files from Meteocode and Bulletin files

## Programs
- `buildJSON.py` : main program (TODO: allow command line calling)
- `parseMeteocode.py` : parse a Meteocode file to produce a JSON structure
- `ppJson.py` : pretty print of a JSON that I find better than the standard one

## Directory structure

NB: *for the moment, only a small directory was created for testing and developing*

The variable `baseDir` should be in front of those directories  
`*` stands for `FP(TO|CN)`*MM*.*dd*.*hhmm*`Z`  
where  

- *MM* : month number
- *dd* : day number
- *hh* : hour
- *mm* : minutes

### source 
- Bulletins/201[89]/ont/TRANSMIT*.[ef] : bulletins in English or French
- Bulletins/201[89]/que/TRANSMIT*.[ef]

- Meteocode/201[89]/ont/TRANSMIT*
- Meteocode/201[89]/que/TRANSMIT*

### output
- JSON/201[89]/ont/* : directory with region names
- JSON/201[89]/ont/*.json 
- JSON/2018/que


Guy Lapalme (lapalme@iro.umontreal.ca)
August 2021