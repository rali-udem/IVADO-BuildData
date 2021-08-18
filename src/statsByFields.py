## compute statistics on the Meteocode files
from collections import Counter
import re,sys,glob,json
from ppJson import ppJson

nb=0
nbPara=0
fields=Counter()
vocField={}
vocabulary_en=Counter()
vocabulary_fr=Counter()

skipFields= set(["header","names-en","names-fr","regions","id"])

def stat(json):
    global nb,nbPara,fields,vocabulary_en,vocabulary_fr
    nb+=1
    for field in json:
        fields[field]+=1
        if field in skipFields:continue
        if not field in vocField:
            vocField[field]=Counter()
        if field=="en" or field=="fr":
            strings=[item for dayLists in json[field]["tok"]
                             for l in json[field]["tok"][dayLists]
                                for item in l if re.fullmatch("[-A-Za-zÀ-ÿ]+",item)]
        else:
            strings=[item for sublist in json[field] for item in sublist if isinstance(item,str)]
        # print(strings)
        for string in strings:
            vocField[field][string]+=1
    
def showCounter(indent,counter):
    for (key,val) in sorted(counter.items(),key=lambda kv:kv[1],reverse=True):
        print("%s%-25s : %9d"%(indent,key,val))

def showStats():
    print("Stats on %d bulletins"%nb)
    print("\n** Fields")
    showCounter("",fields)
    for field in vocField:
        if len(vocField[field])>0:
            print("\n** ",field)
            showCounter("  ",vocField[field])



## running statistics on files given as argument
if len(sys.argv)==1:
    files=["/Users/lapalme/Desktop/IVADO_scribe/arpi-2021_dev.jsonl",
           "/Users/lapalme/Desktop/IVADO_scribe/arpi-2021_test.jsonl",
           "/Users/lapalme/Desktop/IVADO_scribe/arpi-2021_train.jsonl"]
else:
    files=sys.argv[1:]

for file in files:
    print("reading ",file,file=sys.stderr)
    jsonl=open(file,encoding="utf-8")
    for line in jsonl:
        js=json.loads(line.strip())
        # ppJson(sys.stdout,js,0,False)
        stat(js)
showStats()
