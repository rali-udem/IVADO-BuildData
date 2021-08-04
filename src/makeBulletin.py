from datetime import timedelta,datetime
# from jsRealBclass import *

import json

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
def header(codes,beginTime,nextIssue):
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
    return [fmt(s1),fmt(s2),""]


### compute DataFrame statistics 
def getStats(df,field):
    if not df.empty and field in df.columns:
        serie=df[field]
        if not pd.api.types.is_numeric_dtype(serie):return None
        return {"min":serie.min(),
                "idxmin":serie.idxmin(),
                "max":serie.max(),
                "idxmax":serie.idxmax(),
                "mean":serie.mean()}
    return None

### generate each aspect of the bulletin
def clouds(df,beginTime):
    if df.empty:return None
    ceilingStats=getStats(df,"ceiling-code")
    cloudStats=getStats(df,"text()")
    showDF("clouds",df,[ceilingStats,cloudStats])
    cloudLevel=df["text()"].mode()[0]
    if cloudLevel>4:
        return S(NP(Adv("mainly"),A("cloudy")))
    elif cloudLevel==0:
        return S(A("clear"))
    else:
        return S(NP(A("variable"),Q("cloudiness")))
    return None

def precipitations(df,beginTime):
    if df.empty:return None
    precipStats=getStats(df,"text()")
    showDF("precipitations",df,[precipStats])
    maxLevel=precipStats["max"]
    if maxLevel==0: return None
    return S(NP(NO(maxLevel), Q("percent"),PP(P("of"),N("chance"),PP(P("of"),N("shower").n("p")))),
             jsrDayPeriod(df["start"][precipStats["idxmax"]],beginTime)) 

def winds(df,beginTime):
    if df.empty:return None
    windStats=getStats(df,"wind-speed/lower-limit")
    if windStats==None: return None
    gustStats=getStats(df,"gust-speed/lower-limit")
    showDF("winds",df,[windStats,gustStats])
    s=S(N("wind"), NO(windStats["max"]),Q("km/h"))
    dirMode=df["direction"].mode()
    if len(dirMode)>0:
        s.add(Q("direction"),1)
    if gustStats==None: return s
    if windStats["max"]<gustStats["max"]:
        s.add(Q("gusting"))
        s.add(PP(P("to"),NO(gustStats["max"]),Q("km/h")))
    return s

def getI(series,value):
    s=series.loc[series==value]
    if s.empty:return None
    return s.index.values[0]

def temperatures(df,beginTime):
    if df.empty:return None
    trends=df["trend"]
    trendStats=getStats(trends)
    tempStats=getStats(df,"lower-limit")
    showDF("temperature",df,[trendStats,tempStats])
    fallI=getI(trends,"fall")
    if fallI!=None:
        return S(N("temperature"),
                 VP(V("fall").t("pr"),
                    PP(P("to"),NO(df["lower-limit"][fallI])),
                    jsrDayPeriod(df["start"][fallI],beginTime)))
    else:
        minI=getI(trends,"min")
        maxI=getI(trends,"max")
        if minI !=None and maxI !=None:
            return S(N("temperature"),
                     VP(V("be").t("f"),
                        PP(P("between"),NO(df["lower-limit"][minI]),
                           C("and"),NO(df["lower-limit"][maxI]))))
        elif minI !=None or maxI!=None:
            return S(N("minimum" if minI!=None else "maximum"),
                     df["lower-limit"][minI if minI!=None else maxI])
    return None
       
### generate a paragraph for a given period of time
def forecast(fc,title,beginTime,endTime):
    def narrow(df):
        if isinstance(df,pd.DataFrame):
            if df.empty:return df
            df=df.loc[df["start"]>=beginTime]
            return df.loc[df["end"]<endTime]
        return pd.DataFrame()
    
    res=[
        clouds(narrow(fc["cloud-list/cloud-cover"]),beginTime),
        precipitations(
               narrow(fc["probability-of-precipitation-list/probability-of-precipitation"]),beginTime),
        winds(narrow(fc["wind-list/wind"]),beginTime),
        temperatures(narrow(fc["temperature-list[@type='air']/temperature-value"]),beginTime),
    ]
    return textwrap.fill(title+".."+" ".join([fmt(s) for s in res if s!=None]),width=70)

## how many hours from the start to the end of today, tonight and tomorrow
hoursToday=13
hoursTonight=19
hoursTomorrow=44

timeZoneHours=5
timeZoneShift=timedelta(hours=timeZoneHours)  # 5 for Montreal time

bName=""
timeZone=None
issueDate=None
nextDate=None

def getHeaderInfo(fc):
    header=fc["header"][0]
    if len(header)==15:
        [bName,emitter,timeZone,bType,issueYear,issueMonth,issueDay,issueTime,_1,
          _2,nextYear,nextMonth,nextDay,nextTime,_3]=header
        issueDate=datetime(issueYear,issueMonth,issueDay,hour=int(issueTime/100),
                            minute=issueTime%100)-timeZoneShift
        print("issue",issueDate)
        nextDate=datetime(nextYear,nextMonth,nextDay,hour=int(nextTime/100),
                            minute=nextTime%100)-timeZoneShift
        print("next",nextDate)
    else:
        print("bad header",header)

def bulletin(jsonFN):
    fc=json.load(open(jsonFN,"r",encoding="utf-8"))
    print("\n *** Generating from:",jsonFN)
    getHeaderInfo(fc)
    
    # beginTime=fc["begin-time"]
    # res=header(fc["codes"],beginTime,fc["next-issue"])
    # res.extend(fc["names-en"])
    # res[-1]=res[-1]+"."  # add full stop at the end of regions
    # res.append(forecast(fc,"Today",beginTime,
    #                     beginTime+timedelta(hours=hoursToday)))
    # res.append(forecast(fc,"Tonight",beginTime+timedelta(hours=hoursToday),
    #                     beginTime+timedelta(hours=hoursTonight)))
    # res.append(forecast(fc,fmt(jsrDay(beginTime+timedelta(days=1))),
    #                     beginTime+timedelta(hours=hoursTonight),
    #                     beginTime+timedelta(hours=hoursTomorrow)))
    # print("\n".join(res))
    # if not showData:
    #     print("---")
    #     print(fc["en"])
    # print("====")

bulletin("/Users/lapalme/Documents/GitHub/IVADO-BuildData/testDir/JSON/2018/ont/FPTO11.01.01.1000Z/r1102a.json")
