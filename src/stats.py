## compute statistics on the Meteocode files
from collections import Counter
import re,sys,glob,json

nb=0
nbPara=0
fields=Counter()
vocabulary_en=Counter()
vocabulary_fr=Counter()

def stat(json):
    global nb,nbPara,fields,vocabulary_en,vocabulary_fr
    nb+=1
    for field in json:
        fields[field]+=1
    if "en" in json:
        for word in re.split(r"\W+",json["en"]):
            if not re.match(r"^(\d|\s)+$",word):
                vocabulary_en[word]+=1
        for word in re.split(r"\W+",json["fr"]):
            if not re.match(r"^(\d|\s)+$",word):
                vocabulary_fr[word]+=1

def showStats():
    print("Stats on %d bulletins"%nb)
    print("\n** Fields")
    showCounter(fields)
    print("\n** English vocabulary")
    showCounter(vocabulary_en)
    print("\n** French vocabulary")
    showCounter(vocabulary_fr)

def showCounter(counter):
    for (key,val) in sorted(counter.items(),key=lambda kv:kv[1],reverse=True):
        print("%-15s:%6d"%(key,val))


files=glob.glob("/Users/lapalme/Documents/GitHub/IVADO-BuildData/testDir/JSON/2018/ont/*/*.json")
for file in files:
    stat(json.load(open(file,encoding="utf-8")))
showStats()
