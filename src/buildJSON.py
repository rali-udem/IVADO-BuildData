from parseMeteocode import parseMeteocode,showObj
from ppJson import ppJson

import glob,os,json,re, sys

baseDir="/Users/lapalme/Documents/GitHub/IVADO-BuildData/testDir"

## get text of the bulletin for the region name and build a structure with the text,
## the key is the first line with the region name without the the ending "."
def getBulletins(fileFN):
    bulletins={}
    paras=open(fileFN,encoding="latin-1").read().split("\n\n")
    for para in paras[1:-1]:
        key=para[:para.index("\n")]
        if key.endswith("."):key=key[:-1]
        bulletins[key]=para
    # print(bulletins)
    return bulletins

## find a single bulletin whose key is name 
def getBulletin(bulletins,name):
    if name in bulletins:
        return bulletins[name]
    else:
        print("no bulletin:",name)
        return "** no bulletin **"
## 
codeRegions=json.load(open(baseDir+"/codesRegions.json","r",encoding="utf-8"))

def getRegionName(regionNo,lang):
    if regionNo not in codeRegions:
        print("region not found",regionNo)
        return f"** {regionNo} **"
    else:
        return codeRegions[regionNo][lang]

## from obj stored on file jsonFN
##   create a directory of separate bulletin json file with the corresponding English and French bulletins
ignoredKeys=set(["pol_NO","pol_NO2","pol_O3","pol_PM10","pol_PM25","pol_SO2"])
def combineBulletin(jsonFN,obj):
    m = re.match(r"(?P<baseDir>.*)JSON(?P<yearProv>.*?)(?P<fileName>TRANSMIT.*).json",jsonFN)
    if m==None:
        print("no match for JSON file Name",jsonFN)
        sys.exit(1)
    bulletinName=f'{m.group("baseDir")}Bulletins{m.group("yearProv")}{m.group("fileName")}'
    # print(bulletinName)
    en=getBulletins(bulletinName+".e")
    fr=getBulletins(bulletinName+".f")
    
    header=obj[0]["entete"]
    for iRegion in range(1,len(obj)):
        res={"header":header}
        regionObj=obj[iRegion]
        regionNos=regionObj["regions"][0]
        res["names-en"]= [getRegionName(regionNo,"en") for regionNo in regionNos]
        res["names-fr"]= [getRegionName(regionNo,"fr") for regionNo in regionNos]
        for key,val in regionObj.items():
            if key not in ignoredKeys:
                res[key]=val
        res["en"]=getBulletin(en,res["names-en"][0])
        res["fr"]=getBulletin(fr,res["names-fr"][0])
        regionJSONdir=f'{m.group("baseDir")}JSON{m.group("yearProv")}{m.group("fileName")[9:]}'
        if not os.path.exists(regionJSONdir):
            os.makedirs(regionJSONdir)
        regionJSONFN=f"{regionJSONdir}/{regionNos[0]}.json"
        ppJson(open(regionJSONFN,"w",encoding="utf-8"),res,0,False)


## check parsing of a single file
# mc=glob.glob(f"{baseDir}/Meteocode/2018/ont/*")[0]
# print(mc)
# showObj(parseMeteocode(mc))

def makeJSON(year,prov):
    meteocodeDir=f'{baseDir}/Meteocode/{year}/{prov}/'
    jsonDir=f'{baseDir}/JSON/{year}/{prov}/'
    bulletinFNs=sorted(glob.glob(meteocodeDir+"*"))
    print(len(bulletinFNs),"bulletins")
    for bulletinFN in bulletinFNs:
        obj=parseMeteocode(bulletinFN)
        jsonFN=jsonDir+bulletinFN[len(meteocodeDir):]+".json"
        print("processing",jsonFN)
        if not os.path.exists(jsonFN):
            ppJson(open(jsonFN,"w"),obj,0,False)
            combineBulletin(jsonFN,obj)
            print("added",jsonFN)

if __name__ == '__main__':
    makeJSON("2018","ont")
