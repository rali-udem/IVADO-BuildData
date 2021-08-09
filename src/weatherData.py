## Weather data
##   the organization and notation is loosely adapted from Python Pandas

tzHours=5 ## should be the same value as in makeBulletin

def hour(h):
    h=h-tzHours
    if h<24: return str(h)+"h"
    return ["","+","⧺","⧻"][int(h/24)]+str(h%24)+"h"

def showLine(line,colWidths):
    return "%5s "%hour(line[0])+"%5s "%hour(line[1])+" ".join(f"%{colWidths[i]}s"%line[i] for i in range(2,len(line)) )

class WeatherData:
    """
WeatherData: 
  parameters
    title   : used for labeling the data
    columns : column names
    fc      : all lines of a forecast (the first two values must be start and end "hour" in UTC)
    beginHour : start time of the forecast
    endHour   : end time of the forecast 
    beginTime : datetime of the issue time
    text      : text of the scribe forecast
    
  instances variables:
    data    : selected lines within [beginHour,endHour)
    colIndex : mapping between names and column index
"""
    def __init__(self, title, columns, fc, beginHour,endHour,beginTime,text):
        self.title=title;
        self.columns=["start","  end"]+columns
        self.colIndex={key:i for key,i in zip(self.columns,range(0,len(self.columns)))}
        self.data = list(filter(lambda line: beginHour<line[1] and endHour>line[0],fc))
        self.beginTime=beginTime
        self.text=text
    

    def __str__(self):
        res = ["**"+self.title]
        if not self.empty():
            nbCols=len(self.data[0])
            colWidths=[len(col) for col in self.columns[:nbCols]]
            ## compute max width of columns
            for line in self.data:
                for i in range(2,nbCols):
                    colWidths[i]=max(len(str(line[i])),colWidths[i])
            fmt=" ".join(f"%{colWidths[i]}s" for i in range(0,nbCols))
            # output column names and values
            res.append(fmt%tuple(self.columns[:nbCols]))
            for line in self.data:
                res.append(fmt%tuple([hour(line[0]),hour(line[1])]+line[2:nbCols]))
        res.append("===")
        return "\n".join(res)
    
    ## useful for debugging
    def raw(self):
        res=[str(self.columns)]
        for line in self.data:
            res.append(str(line))
        return "\n".join(res)

    ## get a serie corresponding to a column (index by number or column name)
    def __getitem__(self,key):
        if type(key) is str: key=self.colIndex[key]
        return [line[key] for line in self.data]
    
    def empty(self):
        return len(self.data)==0
    
    def size(self):
        return len(self.data)
    
    def getText(self):
        return self.text
    