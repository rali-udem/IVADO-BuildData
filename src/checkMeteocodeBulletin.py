import glob,os,json,re, sys

baseDir="/Users/lapalme/Documents/GitHub/IVADO-BuildData/testDir"
baseDir="/Users/lapalme/Desktop/IVADO_scribe"

def matchMeteoBulletin(year,prov):
    meteocodes=glob.glob(f'{baseDir}/Meteocode/{year}/{prov}/*')
    bulletins=glob.glob(f'{baseDir}/Bulletin/{year}/{prov}/*')
    
    meteocodesSet=set(meteocodes)
    bulletinsSet=set(bulletins)
    nb=0
    print("check missing bulletins from %d Meteocodes in %s/%s"%(len(meteocodes),year,prov))
    for meteocode in meteocodes:
        fn=meteocode.replace("Meteocode","Bulletin")
        if fn+".e" not in bulletinsSet:
            print("missing",fn+".e")
            nb+=1
        if fn+".f" not in bulletinsSet:
            print("missing",fn+".f")
            nb+=1
    print("%d missing bulletins"%nb)
    print("check missing Meteocodes from %d bulletins in %s/%s"%(len(bulletins),year,prov))
    nb=0
    for bulletin in bulletins:
        fn=bulletin.replace("Bulletin","Meteocode")[:-2]
        if fn not in meteocodesSet:
            print("missing",fn)
            nb+=1
    print("%d missing Meteocodes"%nb)

matchMeteoBulletin("2018","ont")
matchMeteoBulletin("2018","que")
matchMeteoBulletin("2019","ont")
matchMeteoBulletin("2019","que")
