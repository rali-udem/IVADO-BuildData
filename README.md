# Create JSON data files from Meteocode and Bulletin files

## Programs in `src` directory
- `buildJSON.py` : main program (TODO: allow command line calling)
- `buildRegionCodes.py` : create *data*/`codeRegions.json` from *data*/`regions.ont.txt` and *data*/`regions.que.txt`
- `checkMeteocodeBulletin.py` : sanity check between names of files in `Meteocode` and `Bulletin` directories
- `makeBulletin.py` : create a bulletin using the jsRealB realiser (work in progress)
- `make_complete_json.py` : create json files for all Meteocode and Bulletin file
- `parseMeteocode.py` : parse a Meteocode file to produce a JSON structure
- `ppJson.py` : pretty print of a JSON in a form that is more compact and readable than the standard Python `pprint`
- `stats.py` : compute statistics on the fields of the json files and the vocabulary used in the bulletins 

## *data* directory structure

NB: *for the moment, only a small directory was created for testing and developing*

The variable `baseDir` should be in front of those directories  
`*` stands for `FP(TO|CN)`*MM*.*dd*.*hhmm*`Z`  
where  

- *MM* : month number
- *dd* : day number
- *hh* : hour
- *mm* : minutes

### source 
- Bulletins/201[89]/ont/TRANSMIT*.[ef] : Ontario bulletins in English or French
- Bulletins/201[89]/que/TRANSMIT*.[ef] : Québec bulletins in English or French

- Meteocode/201[89]/ont/TRANSMIT* : Ontario meteocode 
- Meteocode/201[89]/que/TRANSMIT* : Québec meteocode 

### output
- JSON/201[89]/ont/* : directory with region names
- JSON/201[89]/ont/*.json : created json files 
- JSON/201[89]/que/* : directory with region names
- JSON/201[89]/que/*.json : created json files 


Guy Lapalme (lapalme@iro.umontreal.ca)
Fabrizio Gotti (gottif@iro.umontreal.ca)
August 2021