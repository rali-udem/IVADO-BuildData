## compute statistics on the Meteocode files
from collections import Counter
import re,sys,glob,json

nb=0
nbPara=0
fields=Counter()
vocField={}
vocabulary_en=Counter()
vocabulary_fr=Counter()

skipFields= set(["header","names-en","names-fr","en","fr","regions"])

def stat(json):
    global nb,nbPara,fields,vocabulary_en,vocabulary_fr
    nb+=1
    for field in json:
        fields[field]+=1
        if field in skipFields:continue
        if not field in vocField:
            vocField[field]=Counter()
        strings=[item for sublist in json[field] for item in sublist if isinstance(item,str)]
        # print(strings)
        for string in strings:
            vocField[field][string]+=1
    
def showCounter(indent,counter):
    for (key,val) in sorted(counter.items(),key=lambda kv:kv[1],reverse=True):
        print("%s%-15s:%6d"%(indent,key,val))

def showStats():
    print("Stats on %d bulletins"%nb)
    print("\n** Fields")
    showCounter("",fields)
    for field in vocField:
        if len(vocField[field])>0:
            print("\n** ",field)
            showCounter("  ",vocField[field])

files=glob.glob("/Users/lapalme/Documents/GitHub/IVADO-BuildData/testDir/JSON/2018/ont/*/*.json")
for file in files:
    stat(json.load(open(file,encoding="utf-8")))
showStats()
