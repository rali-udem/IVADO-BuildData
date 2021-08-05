## adapted from https://docs.python.org/3/library/re.html#writing-a-tokenizer
from typing import NamedTuple
import re

class Token(NamedTuple):
    type: str
    value: str
    line: int
    column: int

def tokenize(code):
    keywords = {'IF', 'THEN', 'ENDIF', 'FOR', 'NEXT', 'GOSUB', 'RETURN'}
    token_specification = [
        ('FLOAT',    r'-?\d+\.\d+'),  # decimal number
        ('INT',      r'-?\d+'),  # Integer 
        ('OPEN',     r'\('),           # open parenthesis
        ('CLOSE',    r'\)'),            # close parenthesis
        ("COLON",    r':'),
        ("STOP",     r'\.'),
        ("SEMICOLON",r";"),
        ('ID',       r'[A-Za-z"][A-Za-z0-9_"\.]*'),    # Identifiers
        ('NEWLINE',  r'\n'),           # Line endings
        ('SKIP',     r'[ \t]+'),       # Skip over spaces and tabs
        ('MISMATCH', r'.'),            # Any other character
    ]
    tok_regex = '|'.join(['(?P<%s>%s)' % pair for pair in token_specification])
    line_num = 1
    line_start = 0
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start
        if kind == 'NUMBER':
            value = float(value) if '.' in value else int(value)
        elif kind == 'ID' and value in keywords:
            kind = value
        elif kind == 'NEWLINE':
            line_start = mo.end()
            line_num += 1
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} unexpected on line {line_num}')
        # print(kind,value,line_num,column)
        yield Token(kind, value, line_num, column)

## parsing of Meteocode
##  using the following grammar (approximate...)
##   res    ::= {region} "."
##   region ::= {para}  ## separated by a para starting with an ID
##   para   ::= paraId: {list} ";"
##   list   ::= "(" {float | int | id | list}  ")"
##
##  the result is an object whose keys are paraId and value list of value

def check(token,type):
    if token.type != type:
        print("%d.%d:%s expected but found %s:%s"%(token.line,token.column,type,token.type,token.value))
        raise Exception

def parseList(tokenizer,token):
    check(token,"OPEN")
    token=next(tokenizer)
    val=[]
    while token.type!="CLOSE":
        if token.type=="FLOAT":
            val.append(float(token.value))
        elif token.type=="INT":
            val.append(int(token.value))
        elif token.type=="OPEN":
            val.append(parseList(tokenizer,token))
        else:
            val.append(token.value)
        token=next(tokenizer)
    return val

def parsePara(tokenizer,token):
    val=[]
    check(token,"COLON")
    token=next(tokenizer)
    while token.type!="SEMICOLON":
        val.append(parseList(tokenizer,token))
        token=next(tokenizer)
    return val
    
def parseRegion(tokenizer,token):
    try:
        res={}
        key=token.value
        token=next(tokenizer)
        while True:
            res[key]=parsePara(tokenizer,token)
            token=next(tokenizer);
            if token.type=="ID" and token.value=="regions":
                return (res,token)
            else:
                key=token.value
                token=next(tokenizer)
    except StopIteration:
        return (res,None)

def parseMeteocode(mcFileName):
    tokenizer=tokenize(open(mcFileName,"r",encoding="latin-1").read())
    res=[]
    token=next(tokenizer)
    while True:
        (region,token)=parseRegion(tokenizer,token)
        res.append(region)
        if token==None or token.type=="STOP": break
    return res

### for debugging parsing
def showList(l): # show only first and last elements of a long list
    if len(l)<3:
        return str(l)
    else:
        return "[%s <%d> %s]"%(l[0],len(l)-2,l[-1])

def showRegion(region):
    return '\n{%s}'%"\n ".join([key+":"+showList(val) for key,val in region.items()])

def showObj(obj):
    for region in obj:
        print(showRegion(region))