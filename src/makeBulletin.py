from datetime import timedelta,datetime
from jsRealBclass import *
from weatherData import WeatherData

import json, textwrap, re

showData=True

### Text generation
def fmt(jsrExp):
    return textwrap.fill(jsRealB(jsrExp.show(-1)),width=70);

### time generation
def jsrTime(dt):
    return PP(P("at"),
              DT(dt).dOpt({"year":False , "month": False , "date":False , "day":False , 
                           "hour":True , "minute":True , "second":False , 
                           "nat":False, "det":False, "rtime":False}),
              Q("EST"))

def jsrDay(dt):
    return  DT(dt).dOpt({"year":False , "month": False , "date":False , "day":True , 
                           "hour":False , "minute":False , "second":False , 
                           "nat":False, "det":False, "rtime":False})
    
def jsrDate(dt):
    return  DT(dt).dOpt({"year":True , "month": True , "date":True , "day":False , 
                           "hour":False , "minute":False , "second":False , 
                           "nat":True, "det":False, "rtime":False})


def jsrHour(h):
    if h in [0,6]:
        return PP(P("during"),NP(D("the"),N("night")))
    if h in [7,10]:
        return PP(P("in"),NP(D("the"),N("morning")))
    if h in [11,12,13]:
        return PP(P("around"),N("noon"))
    if h in [14,18]:
        return PP(P("in"),NP(D("the"),N("afternoon")))
    if h in [19,24]:
        return PP(P("in"),NP(D("the"),N("evening")))
    
dayPeriods=[(0,5,lambda:NP(N("night"))),
            (5,9,lambda:NP(Adv("early"),N("morning"))),
            (9,12,lambda:NP(N("morning"))),
            (12,18,lambda:NP(N("afternoon"))),
            (18,24,lambda:NP(N("tonight")))
            ]

def jsrDayPeriod(dt,beginTime):
    hour=dt.hour
    # print("hour",hour)
    isTomorrow=dt.toordinal()>beginTime.toordinal()
    for (s,e,jsrExp) in dayPeriods:
        if hour in range(s,e):
            exp=jsrExp()
            if isTomorrow:
                return exp.add(N("tomorrow"),0)
            elif s!=6:
                return exp.add(D("this"),0)
    
###   global header information
def header(beginTime,nextIssue):
    s1=S(N("forecast"),VP(V("issue").t("pp"),
                              PP(P("by"),NP(N("environment").cap(True),Q("Canada"))),
                              jsrDay(beginTime),
                              jsrTime(beginTime),
                              jsrDate(beginTime),
                              PP(P("for"),
                                 CP(C("and"),N("today"),jsrDay(beginTime+timedelta(days=1))))))                                             
    s2=S(NP(D("the"),Adv("next"),V("schedule").t("pp"),N("forecast"),
         VP(V("be").t("f"),V("issue").t("pp"),
            jsrTime(nextIssue))))
    return ["===",fmt(s1),fmt(s2),""]

## taken from https://stackoverflow.com/questions/31364464/python-3-find-the-mode-of-a-list/31364691#31364691
from collections import Counter
def mode(l):
    counter = Counter(l)
    max_count = max(counter.values())
    return [item for item, count in counter.items() if count == max_count]

### generate each aspect of the bulletin
#  ciel: start end neb-start neb-end {ceiling-height}
def clouds(tuples):
    print(tuples)
    if tuples.empty():return None
    nebs = tuples["neb-start"]
    cloudLevel=mode(nebs)[0]
    print("cloudlevel",cloudLevel)
    if cloudLevel>4:
        return S(NP(Adv("mainly"),A("cloudy")))
    elif cloudLevel==0:
        return S(A("clear"))
    else:
        return S(NP(A("variable"),Q("cloudiness")))
    return None

# pcpn : start end certainty code type intensity frequency exception?
def precipitations(tuples):
    print(tuples)
    if tuples.empty():return None
    # maxLevel=precipStats["max"]
    # if maxLevel==0: return None
    # return S(NP(NO(maxLevel), Q("percent"),PP(P("of"),N("chance"),PP(P("of"),N("shower").n("p")))),
             # jsrDayPeriod(df["start"][precipStats["idxmax"]],beginTime))

# vents : start end direction modif? speed value exception?
def winds(tuples):
    print(tuples)
    if tuples.empty():return None
    # if df.empty:return None
    # windStats=getStats(df,"wind-speed/lower-limit")
    # if windStats==None: return None
    # gustStats=getStats(df,"gust-speed/lower-limit")
    # showDF("winds",df,[windStats,gustStats])
    # s=S(N("wind"), NO(windStats["max"]),Q("km/h"))
    # dirMode=df["direction"].mode()
    # if len(dirMode)>0:
    #     s.add(Q("direction"),1)
    # if gustStats==None: return s
    # if windStats["max"]<gustStats["max"]:
    #     s.add(Q("gusting"))
    #     s.add(PP(P("to"),NO(gustStats["max"]),Q("km/h")))
    # return s

#    temp : start end trend value
def temperatures(tuples):
    print(tuples)
    if tuples.empty():return None
    # if df.empty:return None
    # trends=df["trend"]
    # trendStats=getStats(trends)
    # tempStats=getStats(df,"lower-limit")
    # showDF("temperature",df,[trendStats,tempStats])
    # fallI=getI(trends,"fall")
    # if fallI!=None:
    #     return S(N("temperature"),
    #              VP(V("fall").t("pr"),
    #                 PP(P("to"),NO(df["lower-limit"][fallI])),
    #                 jsrDayPeriod(df["start"][fallI],beginTime)))
    # else:
    #     minI=getI(trends,"min")
    #     maxI=getI(trends,"max")
    #     if minI !=None and maxI !=None:
    #         return S(N("temperature"),
    #                  VP(V("be").t("f"),
    #                     PP(P("between"),NO(df["lower-limit"][minI]),
    #                        C("and"),NO(df["lower-limit"][maxI]))))
    #     elif minI !=None or maxI!=None:
    #         return S(N("minimum" if minI!=None else "maximum"),
    #                  df["lower-limit"][minI if minI!=None else maxI])
    return None

## UV_index values: info taken from
#  https://www.canada.ca/en/environment-climate-change/services/weather-health/uv-index-sun-safety/about.html
#      Low (0-2), Moderate (3-5), High (6-7), Very High (8-10), and Extreme (11+)
uv_ranges= [(2,A("low")), (5, A("moderate")), (7,A("high")), 
            (10,AP(Adv("very"),Adv("high"))), (1000,A("extreme"))]
#     indice_uv : start end value
def uv_index(tuples):
    print(tuples)
    print(tuples.getText())
    if tuples.empty():return None
    uvVal=round(max(tuples["value"]))
    print(uvVal)
    for high,expr in uv_ranges:
        if uvVal<=high: 
            return S(Q("UV"),N("index"),VP(V("be"),NO(uvVal),C("or"),expr))
    return None

    
### generate a paragraph for a given period of time
def forecast(fc,title,beginHour,endHour,text):
    res=[
        clouds        (WeatherData("clouds-fc['ciel]",["neb-start","neb-end","ceiling-height"],
                                   fc["ciel"],beginHour,endHour,beginTime,text)),
        precipitations(WeatherData("precipitations-fc['prob'][0][2:]",
                                   ["certainty","code","type","intensity", "frequency", "exception"],
                                   fc["prob"][0][2:],beginHour,endHour,beginTime,text)),
        winds         (WeatherData("winds-fc['vents']",["direction", "modif?", "speed", "value", "exception?"],
                                   fc["vents"],beginHour,endHour,beginTime,text)),
        temperatures  (WeatherData("temperatures-fc['temp']",["trend", "value"],
                                   fc["temp"],beginHour,endHour,beginTime,text)),
        uv_index      (WeatherData("indice_uv-fc['indice_uv']",["value"],
                                   fc["indice_uv"],beginHour,endHour,beginTime,text))
    ]
    return textwrap.fill(title+".."+" ".join([fmt(s) for s in res if s!=None]),width=70)

## how many hours from the start to the end of today, tonight and tomorrow
hoursToday=13
hoursTonight=19
hoursTomorrow=44

tzHours=5
tzShift=timedelta(hours=tzHours)  # 5 for Montreal time

bulletinName=""
tz=None
beginTime=None

def getTimeInfo(fc):
    header=fc["header"][0]
    if len(header)==15:
        [bulletinName,emitter,tz,bType,issueYear,issueMonth,issueDay,issueTime,_1,
          _2,nextYear,nextMonth,nextDay,nextTime,_3]=header
        beginTime=datetime(issueYear,issueMonth,issueDay,hour=int(issueTime/100),
                            minute=issueTime%100)-tzShift
        nextTime=datetime(nextYear,nextMonth,nextDay,hour=int(nextTime/100),
                            minute=nextTime%100)-tzShift
    else:
        print("bad header",header)
    return (beginTime,nextTime)

def bulletin(jsonFN):
    global beginTime
    fc=json.load(open(jsonFN,"r",encoding="utf-8"))
    texts=[t.strip().replace('\n'," ") for t in re.split(r"[A-Z][a-z]+\.\.",fc["en"])]
    print("\n *** Generating from:",jsonFN)
    (beginTime,nextTime)=getTimeInfo(fc)
    
    res=header(beginTime,nextTime)
    res.extend(fc["names-en"])
    res[-1]=res[-1]+"."  # add full stop at the end of regions
    res.append(forecast(fc,"Today",0+tzHours,hoursToday+tzHours,texts[1]))
    # res.append(forecast(fc,"Tonight",beginTime+timedelta(hours=hoursToday),
    #                     beginTime+timedelta(hours=hoursTonight),texts[2]))
    # res.append(forecast(fc,fmt(jsrDay(beginTime+timedelta(days=1))),
    #                     beginTime+timedelta(hours=hoursTonight),
    #                     beginTime+timedelta(hours=hoursTomorrow),texts[3]))
    print("\n".join(res))
    print("\n** original\n",fc["en"])
    # if not showData:
    #     print("---")
    #     print(fc["en"])
    # print("====")

bulletin("/Users/lapalme/Documents/GitHub/IVADO-BuildData/testDir/bulletin1.json")
# bulletin("/Users/lapalme/Documents/GitHub/IVADO-BuildData/testDir/JSON/2018/ont/FPTO11.01.01.1000Z/r1102a.json")
