import os, struct, json, astor, sys
from ast import *
from collections import defaultdict, OrderedDict

json_data = open('static_db/gg_revelator/commandDB.json').read()
commandDB = json.loads(json_data)
json_data = open('static_db/gg_revelator/characters.json').read()
characters = json.loads(json_data)
commandCounts = defaultdict(int)
commandCalls = defaultdict(list)
MODE = "<"
GAME = "gg_rev"
uponLookup = {
    0:"IMMEDIATE"
}
slotLookup = {
    212:"IS_STYLISH"
}
def getUponName(cmdData):
    if cmdData == 0:
        return "IMMEDIATE"
    return str(cmdData)
def getSlotName(cmdData):
    if cmdData == 212:
        return "IS_STYLISH"
    return str(cmdData)
def sanitizer(command):
    def sanitize(s):
        if isinstance(s,str):
            s = "'{0}'".format(s.strip("\x00"))
        elif command and "hex" in commandDB[str(command)]:
            s = hex(s)
        return str(s).strip("\x00")
    return sanitize
def pysanitizer(command):
    def sanitize(s):
        if isinstance(s,str):
            s = "{0}".format(s.strip("\x00"))
        elif command and "hex" in commandDB[str(command)]:
            s = hex(s)
        return str(s).strip("\x00")
    return sanitize
def parse_bbscript_routine(f,end = -1):
    global MODE,charName,j,astRoot
    currentCMD = -1
    currentIndicator = "_PRE"
    currentFrame = 1
    currentIndent = 0
    astStack = [astRoot.body]
    uponindent = 0
    inIf = 0
    inUpon = 0
    while f.tell() != end:

        loc = f.tell()
        currentCMD, = struct.unpack(MODE+"I",f.read(4))
        if 'endBlock' in commandDB[str(currentCMD)]:
                currentIndent -= 1
        commandCounts[currentCMD] += 1

        dbData = commandDB[str(currentCMD)]
        if "name" not in dbData:
            dbData["name"] = "Unknown{0}".format(currentCMD)
        if "format" not in commandDB[str(currentCMD)]:
            cmdData = [f.read(commandDB[str(currentCMD)]["size"]-4).encode("hex")]
        else:
            cmdData = list(struct.unpack(MODE+dbData["format"],f.read(struct.calcsize(dbData["format"]))))
        commandCalls[currentCMD].append((characters[charName],currentIndicator,currentFrame,"{0}({1})".format(dbData["name"],",".join(map(sanitizer(currentCMD),cmdData)))))
        if dbData['name'] == 'startState':
            currentContainerntIndicator = cmdData[0].strip("\x00")
            currentContainer = []
            j["Functions"].append({'type':'state','name':cmdData[0].strip("\x00"),'commands':currentContainer})
        elif dbData["name"] == "startSubroutine":
            currentIndicator = cmdData[0].strip("\x00")
            currentContainer = []
            j["Functions"].append({'type':'subroutine','name':cmdData[0].strip("\x00"),'commands':currentContainer})
        elif 'endBlock' in dbData:
            pass
        else:
            currentContainer.append({'id':currentCMD,'params':map(pysanitizer(currentCMD),cmdData)})
        comment = None
        #AST STUFF
        if GAME != "gg_rev":
            pass
        elif dbData['name'] == 'startState':
            astStack[-1].append(FunctionDef(cmdData[0].strip("\x00"),arguments([],None,None,[]),[],[Name(id="State")]))
            astStack.append(astStack[-1][-1].body)
        elif dbData['name'] == 'startSubroutine':
            astStack[-1].append(FunctionDef(cmdData[0].strip("\x00"),arguments([],None,None,[]),[],[Name(id="Subroutine")]))
            astStack.append(astStack[-1][-1].body)
        elif dbData['name'] == 'upon':
            astStack[-1].append(FunctionDef(dbData['name']+"_"+getUponName(cmdData[0]),arguments([],None,None,[]),[],[]))
            astStack.append(astStack[-1][-1].body)
        elif dbData['name'] == 'if' and cmdData[1] == 0:
            tmp = astStack[-1].pop()
            if not hasattr(tmp,"value"):
                tmp = Expr(tmp)
            astStack[-1].append(If(tmp.value,[],[]))
            astStack.append(astStack[-1][-1].body)
        elif dbData['name'] == 'if':
            tmp = Name(id="SLOT_"+getSlotName(cmdData[1]))
            astStack[-1].append(If(tmp,[],[]))
            astStack.append(astStack[-1][-1].body)
        elif dbData['name'] == 'op' and cmdData[0] in [9,10,11,12,13,16]:
            if(cmdData[1] == 2):
                lval = Name(id="SLOT_"+str(cmdData[2]))
            else:
                lval = Num(cmdData[2])
            if(cmdData[3] == 2):
                rval = Name(id="SLOT_"+str(cmdData[4]))
            else:   
                rval = Num(cmdData[4])
            if cmdData[0] == 9:
                op = Eq()
            if cmdData[0] == 10:
                op = Gt()
            if cmdData[0] == 11:
                op = Lt()
            if cmdData[0] == 12:
                op = GtE()
            if cmdData[0] == 13:
                op = LtE()
            if cmdData[0] == 16:
                op = NotEq()
            tmp = Expr(Compare(lval,[op],[rval]))
            astStack[-1].append(If(tmp.value,[],[]))
            astStack.append(astStack[-1][-1].body)
        elif dbData['name'] == 'StoreValue':
            if(cmdData[0] == 2):
                lval = Name(id="SLOT_"+str(cmdData[1]))
            else:
                lval = Num(cmdData[1])
            if(cmdData[2] == 2):
                rval = Name(id="SLOT_"+str(cmdData[3]))
            else:
                rval = Num(cmdData[3])
            tmp = Assign([lval],rval)
            astStack[-1].append(tmp)
        elif dbData['name'] == 'ModifyVar_' and cmdData[0] in [0,1,2,3]:
            if(cmdData[1] == 2):
                lval = Name(id="SLOT_"+str(cmdData[2]))
            else:
                lval = Num(cmdData[2])  
            if(cmdData[3] == 2):
                rval = Name(id="SLOT_"+str(cmdData[4]))
            else:
                rval = Num(cmdData[4])
            if cmdData[0] == 0:
                op = Add()
            if cmdData[0] == 1:
                op = Sub()
            if cmdData[0] == 2:
                op = Mult()
            if cmdData[0] == 3:
                op = Div()
            tmp = Assign([lval],BinOp(lval,op,rval))
            astStack[-1].append(tmp)
        elif dbData['name'] == 'ifNot' and cmdData[1] == 0:
            tmp = astStack[-1].pop()
            if not hasattr(tmp,"value"):
                tmp = Expr(tmp)
            astStack[-1].append(If(UnaryOp(Not(),tmp),[],[]))
            astStack.append(astStack[-1][-1].body)
        elif dbData['name'] == 'ifNot':
            tmp = Name(id="SLOT_"+getSlotName(cmdData[1]))
            astStack[-1].append(If(UnaryOp(Not(),tmp),[],[]))
            astStack.append(astStack[-1][-1].body)
        elif dbData['name'] == 'else':
            ifnode = astStack[-1][-1]
            astStack.append(ifnode.orelse)
        elif 'endBlock' in dbData:
            if inIf == 0 and dbData['name'] == 'endIf':
                continue
            elif inUpon == 0 and dbData['name'] == 'endUpon':
                continue
            else:
                if len(astStack[-1]) == 0:
                    astStack[-1].append(Pass())
                if len(astStack) > 1:
                    astStack.pop()
                    if dbData['name'] == 'endState' or dbData['name'] == 'endSubroutine':
                        while(inUpon > 0):
                            astStack.pop()
                            inUpon -= 1
                        while(inIf > 0):
                            astStack.pop()
                            inIf -= 1
                    if len(astStack) == 1:
                        lastFunc = j["Functions"][-1]
                        j["FunctionsPy"].append({"type":lastFunc["type"],"name":lastFunc["name"],"src":astor.to_source(astStack[-1][-1])})
                else:
                    print "\tasterror",currentIndicator
                    astStack[-1].append(Expr(Call(Name(id=dbData["name"]),map(sanitizer(currentCMD),cmdData),[],None,None)))
                if dbData['name'] == 'endUpon':
                    inUpon -= 1
                if dbData['name'] == 'endIf':
                    inIf -= 1

        else:
            astStack[-1].append(Expr(Call(Name(id=dbData["name"]),map(sanitizer(currentCMD),cmdData),[],None,None)))
        if GAME == "gg_rev":
            if dbData['name'] == 'sprite':
                #comment = "Frame {0}->{1}".format(currentFrame,currentFrame+cmdData[1])
                currentFrame = currentFrame+cmdData[1]
            if dbData['name'] == "upon":
                param = 1
                if cmdData[0] == 0:
                    comment = "immediate"
            if dbData['name'] == 1393:
                if cmdData[0] == 0x4:
                    comment = "P_BUTTON"
                if cmdData[0] == 0xD:
                    comment = "K_BUTTON"
                if cmdData[0] == 0x16:
                    comment = "S_BUTTON"
                if cmdData[0] == 0x1F:
                    comment = "H_BUTTON"
                if cmdData[0] == 0xAC:
                    comment = "236"
                if cmdData[0] == 0xAD:
                    comment = "623"
                if cmdData[0] == 0xAE:
                    comment = "214"
                if cmdData[0] == 0xAF:
                    comment = "41236"
                if cmdData[0] == 0xB0:
                    comment = "421"
                if cmdData[0] == 0xB1:  
                    comment = "63214"
                if cmdData[0] == 0xB2:
                    comment = "236236"
                if cmdData[0] == 0xB3:
                    comment = "214214"
                if cmdData[0] == 0xBA:
                    comment = "22"
                if cmdData[0] == 0xF8:
                    comment = "632146"

            if comment:
                currentContainer[-1]['comment'] = comment
            if 'startBlock' in dbData:
                currentIndent += 1
            if dbData['name'] in ['if','op','ifNot']:
                inIf += 1
            if dbData['name'] == 'upon':
                inUpon += 1

def parse_bbscript(f,basename,filename,filesize):
    global commandDB,astRoot,charName,j,MODE
    BASE = f.tell()
    charName = f.name[:3]
    astRoot = Module(body=[])
    j = OrderedDict()
    j["Functions"] = []
    j["FunctionsPy"] = []
    FUNCTION_COUNT, = struct.unpack(MODE+"I",f.read(4))
    f.seek(0x24*(FUNCTION_COUNT), 1)
    parse_bbscript_routine(f, os.stat(filename).st_size)
    '''
    for i in range(0,FUNCTION_COUNT):
        f.seek(BASE+4+0x24*i)
        FUNCTION_NAME = f.read(0x20).split("\x00")[0]
        if log: log.write("\n#---------------{0} {1}/{2}\n".format(FUNCTION_NAME,i,FUNCTION_COUNT))
        FUNCTION_OFFSET, = struct.unpack(MODE+"I",f.read(4))
        f.seek(BASE+4+0x24*FUNCTION_COUNT+FUNCTION_OFFSET)
        parse_bbscript_routine(f)
    '''
    py = open(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),filename+".py"),"w")
    py.write(astor.to_source(astRoot))
    py.close()
    return filename,j
if __name__ == '__main__':
    parse_bbscript(open(sys.argv[1], 'rb'), '',sys.argv[1], os.stat(sys.argv[1]).st_size)