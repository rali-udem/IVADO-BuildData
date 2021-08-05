import glob,os,json,re,sys

baseDir=os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../testDir'))

codes={}
for file in glob.glob(f"{baseDir}/regions-*.txt"):
    print(file)
    for line in open(file,"r",encoding="latin-1"):
        [bulletin,region,_,fr,en]=line.strip().split("|")
        codes[region]={
            "bulletin":bulletin,
            "en":en,
            "fr":fr
        }
json.dump(codes,open(f"{baseDir}/codesRegions-new.json","w",encoding="utf-8"),
          sort_keys=True,ensure_ascii=False,indent=2)