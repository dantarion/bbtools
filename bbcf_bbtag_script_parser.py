import os, struct, json, astor,sys
from ast import *
from collections import defaultdict, OrderedDict

json_data=open("static_db/bbcf/commandsDB.json").read()
commandDB = json.loads(json_data)
json_data=open("static_db/bbcf/characters.json").read()
characters = json.loads(json_data)
json_data=open("static_db/bbcf/named_values/move_inputs.json").read()
moveInputs = json.loads(json_data)
json_data=open("static_db/bbcf/named_values/normal_inputs.json").read()
normalInputs = json.loads(json_data)
commandCounts = defaultdict(int)
commandCalls = defaultdict(list)
MODE = "<"
GAME = "bb"
uponLookup = {
    0:"IMMEDIATE",
    1:"STATE_END",
    2:"LANDING",
    3:"CLEAR_OR_EXIT",
    10:"ON_HIT_OR_BLOCK",
}
slotLookup = {
    0: "ReturnVal",
    18: "FrameCounter",
    47: "IsInOverdrive",
    54: "IsInOverdrive2",
    106: "IsInOverdrive3",
    91: "IsPlayer2",
    112:"IsUnlimitedCharacter"
}
def findNamedValue(command, value):
    if commandDB[str(command)]['name'] == 'Move_Input_' or commandDB[str(command)]['name'] == 'CheckInput':
        if str(value) in moveInputs:
            return moveInputs[str(value)]
        return hex(value)
    elif commandDB[str(command)]['name'] == 'Move_Register' and isinstance(value, int):
        decstr = str(value)
        if decstr in normalInputs['grouped_values']:
            return normalInputs['grouped_values'][decstr]
        s = struct.pack('>H', value)
        button_byte, dir_byte = struct.unpack('>BB', s)
        if str(button_byte) in normalInputs['buttonbyte'] and str(dir_byte) in normalInputs['directionbyte']:
            return normalInputs['directionbyte'][str(dir_byte)] + normalInputs['buttonbyte'][str(button_byte)]
        return hex(value)
    elif commandDB[str(command)]['name'] == 'Move_Register' and isinstance(value,str):
        return value

def getUponName(cmdData):
    return uponLookup.get(cmdData,str(cmdData))

def getSlotName(cmdData):
    return slotLookup.get(cmdData,str(cmdData))

def sanitizer(command):
    def sanitize(s):
        if command in [43,14012,14001] and isinstance(s, int):
            s = findNamedValue(command, s)
        elif isinstance(s,str):
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
    while f.tell() != end:

        loc = f.tell()
        currentCMD, = struct.unpack(MODE+"I",f.read(4))
        if currentCMD in [1,5,9,16,55,57,14002]:
            currentIndent -= 1
        indent = " "*4*currentIndent
        commandCounts[currentCMD] += 1

        dbData = commandDB[str(currentCMD)]
        if "name" not in dbData:
            dbData["name"] = "Unknown{0}".format(currentCMD)
        if "format" not in commandDB[str(currentCMD)]:
            cmdData = [f.read(commandDB[str(currentCMD)]["size"]-4).encode("hex")]
        else:
            cmdData = list(struct.unpack(MODE+dbData["format"],f.read(struct.calcsize(dbData["format"]))))
        #commandCalls[currentCMD].append((characters[charName],currentIndicator,currentFrame,"{0}({1})".format(dbData["name"],",".join(map(sanitizer(currentCMD),cmdData)))))
        if currentCMD == 0:
            currentIndicator = cmdData[0].strip("\x00")
            if currentIndicator[0].isdigit():
                currentIndicator = "__"+currentIndicator
            if " " in currentIndicator:
                currentIndicator = currentIndicator.replace(" ","__sp__")
            if '?' in currentIndicator:
                currentIndicator = currentIndicator.replace("?","__qu__")
            if '@' in currentIndicator:
                currentIndicator = currentIndicator.replace("@","__at__")
            currentContainer = []
            j["Functions"].append({'type':'state','name':currentIndicator,'commands':currentContainer})
        elif dbData["name"] == "startSubroutine":
            currentIndicator = cmdData[0].strip("\x00")
            if currentIndicator[0].isdigit():
                currentIndicator = "__"+currentIndicator
            if " " in currentIndicator:
                currentIndicator = currentIndicator.replace(" ","__sp__")
            if '?' in currentIndicator:
                currentIndicator = currentIndicator.replace("?","__qu__")
            if '@' in currentIndicator:
                currentIndicator = currentIndicator.replace("@","__at__")
            currentContainer = []
            j["Functions"].append({'type':'subroutine','name':currentIndicator,'commands':currentContainer})
        elif dbData["name"] in ["endFunction","endSubroutine"]:
            pass
        else:
            currentContainer.append({'id':currentCMD,'params':map(pysanitizer(currentCMD),cmdData)})
        comment = None
        #AST STUFF
        if GAME != "bb":
            pass
        elif currentCMD == 0:
            currentIndicator = cmdData[0].strip("\x00")
            if currentIndicator[0].isdigit():
                currentIndicator = "__"+currentIndicator
            if " " in currentIndicator:
                currentIndicator = currentIndicator.replace(" ","__sp__")
            if '?' in currentIndicator:
                currentIndicator = currentIndicator.replace("?","__qu__")
            if '@' in currentIndicator:
                currentIndicator = currentIndicator.replace("@","__at__")
            astStack[-1].append(FunctionDef(currentIndicator,arguments([],None,None,[]),[],[Name(id="State")]))
            astStack.append(astStack[-1][-1].body)
        elif currentCMD == 8:
            currentIndicator = cmdData[0].strip("\x00")
            if currentIndicator[0].isdigit():
                currentIndicator = "__"+currentIndicator
            if " " in currentIndicator:
                currentIndicator = currentIndicator.replace(" ","__sp__")
            if '?' in currentIndicator:
                currentIndicator = currentIndicator.replace("?","__qu__")
            if '@' in currentIndicator:
                currentIndicator = currentIndicator.replace("@","__at__")
            astStack[-1].append(FunctionDef(currentIndicator,arguments([],None,None,[]),[],[Name(id="Subroutine")]))
            astStack.append(astStack[-1][-1].body)
        elif currentCMD == 15:
            astStack[-1].append(FunctionDef(dbData['name']+"_"+getUponName(cmdData[0]),arguments([],None,None,[]),[],[]))
            astStack.append(astStack[-1][-1].body)
        elif currentCMD == 4 and cmdData[1] == 0:
            if astStack[-1] == []:
                tmp = Name(id="SLOT_"+str(getSlotName(cmdData[1])))
                astStack[-1].append(If(tmp,[],[]))
            else:        
                tmp = astStack[-1].pop()
                if not hasattr(tmp,"value"):
                    tmp = Expr(tmp)
                astStack[-1].append(If(tmp.value,[],[]))
            astStack.append(astStack[-1][-1].body)
        elif currentCMD == 4:
            tmp = Name(id="SLOT_"+str(getSlotName(cmdData[1])))
            astStack[-1].append(If(tmp,[],[]))
            astStack.append(astStack[-1][-1].body)
        elif currentCMD == 18 and cmdData[1] == 0:
            if astStack[-1] == []:
                tmp = Name(id="SLOT_"+str(getSlotName(cmdData[1])))
                astStack[-1].append(If(tmp,[],[]))
            else: 
                tmp = astStack[-1].pop()
                if not hasattr(tmp,"value"):
                    tmp = Expr(tmp)
                astStack[-1].append(If(tmp.value,[],[]))
            astStack[-1][-1].body = [Expr(Call(Name(id="_gotolabel"),[cmdData[0]],[],None,None))]
        elif currentCMD == 18:

            tmp = Name(id="SLOT_"+str(getSlotName(cmdData[2])))
            astStack[-1].append(If(tmp,[],[]))
            astStack[-1][-1].body = [Expr(Call(Name(id="_gotolabel"),[cmdData[0]],[],None,None))]
        elif currentCMD == 40 and cmdData[0] in [9,10,11,12,13]:
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
            tmp = Expr(Compare(lval,[op],[rval]))
            astStack[-1].append(tmp)
        elif currentCMD == 41:
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
        elif currentCMD == 49 and cmdData[0] in [0,1,2,3]:
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
        elif currentCMD == 54 and cmdData[1] == 0:
            if astStack[-1] == []:
                tmp = Name(id="SLOT_"+str(getSlotName(cmdData[1])))
                astStack[-1].append(If(tmp,[],[]))
            else: 
                tmp = astStack[-1].pop()
                if not hasattr(tmp,"value"):
                    tmp = Expr(tmp)
                astStack[-1].append(If(UnaryOp(Not(),tmp.value),[],[]))
            astStack.append(astStack[-1][-1].body)
        elif currentCMD == 54:
            tmp = Name(id="SLOT_"+str(getSlotName(cmdData[1])))
            astStack[-1].append(If(UnaryOp(Not(),tmp),[],[]))
            astStack.append(astStack[-1][-1].body)
        elif currentCMD == 56:
            ifnode = astStack[-1][-1]
            if(isinstance(ifnode, If)):
                astStack.append(ifnode.orelse)
            else:
                astStack.append([])
        elif currentCMD in [1,5,9,16,55,57]:
            if len(astStack[-1]) == 0:
                astStack[-1].append(Pass())
            if len(astStack) > 1:
                astStack.pop()
                if len(astStack) == 1:
                    lastFunc = j["Functions"][-1]
                    j["FunctionsPy"].append({"type":lastFunc["type"],"name":lastFunc["name"],"src":astor.to_source(astStack[-1][-1])})
            else:
                print "\tasterror",currentIndicator
                astStack[-1].append(Expr(Call(Name(id=dbData["name"]),map(sanitizer(currentCMD),cmdData),[],None,None)))
        else:
            astStack[-1].append(Expr(Call(Name(id=dbData["name"]),map(sanitizer(currentCMD),cmdData),[],None,None)))

        if GAME == "bb":
            if currentCMD == 2:
                #comment = "Frame {0}->{1}".format(currentFrame,currentFrame+cmdData[1])
                currentFrame = currentFrame+cmdData[1]
            if currentCMD in [15,29]:
                param = 0
                if currentCMD == 29:
                    param = 1
                if cmdData[0] == 0:
                    comment = "immediate"
                if cmdData[0] == 1:
                    comment = "move end"
                if cmdData[0] == 2:
                    comment = "landing"
                if cmdData[0] == 10:
                    comment = "on hit or block"
            if currentCMD == 4:
                if cmdData[1] == 47:
                    comment = "Overdrive"
                if cmdData[1] == 91:
                    comment = "IsPlayer2"
                if cmdData[1] == 112:
                    comment = "IsUnlimitedCharacter"
            if currentCMD == 14012:
                if cmdData[0] == 0x4:
                    comment = "A_BUTTON"
                if cmdData[0] == 0xD:
                    comment = "B_BUTTON"
                if cmdData[0] == 0x16:
                    comment = "C_BUTTON"
                if cmdData[0] == 0x1F:
                    comment = "D_BUTTON"
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
                if currentCMD in [0,4,8,15,54,56,14001]:
                    currentIndent += 1

def parse_bbscript(f,basename,filename,filesize):
    global commandDB,astRoot,charName,j,MODE
    BASE = f.tell()
    astRoot = Module(body=[])
    j = OrderedDict()
    j["Functions"] = []
    j["FunctionsPy"] = []
    charName = filename[-6:-4]
    FUNCTION_COUNT, = struct.unpack(MODE+"I",f.read(4))
   # f.seek(BASE+4+0x20)
   # initEnd, = struct.unpack(MODE+"I",f.read(4))
   # initEnd = BASE + initEnd+4+0x24*FUNCTION_COUNT
   # initEnd = BASE+filesize
    f.seek(BASE+4+0x24*(FUNCTION_COUNT))
    parse_bbscript_routine(f,os.path.getsize(f.name))
    '''
    for i in range(0,FUNCTION_COUNT):
        f.seek(BASE+4+0x24*i)
        FUNCTION_NAME = f.read(0x20).split("\x00")[0]
        if log: log.write("\n#---------------{0} {1}/{2}\n".format(FUNCTION_NAME,i,FUNCTION_COUNT))
        FUNCTION_OFFSET, = struct.unpack(MODE+"I",f.read(4))
        f.seek(BASE+4+0x24*FUNCTION_COUNT+FUNCTION_OFFSET)
        parse_bbscript_routine(f)
    '''
    if len(sys.argv) == 3:
        outpath = os.path.join(sys.argv[2],filename[:-4] + '.py')
    else:
        outpath = filename[:-4] + '.py'
    py = open(outpath,"wb")
    py.write(astor.to_source(astRoot))
    py.close()
    return filename,j
if __name__ == '__main__':
    if len(sys.argv) != 3 and len(sys.argv) != 2:
        print "Usage:bbcf_script_parser.py scr_xx.bin outdir"
        print "Default output directory if left blank is the current script directory."
    else:
        infn = sys.argv[1]
        f = open(sys.argv[1], 'rb');
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(0)
        parse_bbscript(f,"",f.name,size)
