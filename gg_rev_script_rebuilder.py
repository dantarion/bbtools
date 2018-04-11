import os, struct, json, astor
import sys
from ast import *
from collections import defaultdict, OrderedDict
import gg_rev_script_parser
import named_value_lookup

commandDB  = json.loads(open("static_db/gg_revelator/commandDB.json").read())
characters = json.loads(open("static_db/gg_revelator/characters.json").read())

commandDBLookup = {}

gg_rev_script_parser.commandDB = commandDB
gg_rev_script_parser.characters = characters

for key,data in commandDB.items():
    data["id"] = int(key)
    if "name" in data:
        commandDBLookup[data["name"]] = data
    else:
        commandDBLookup["Unknown"+key] = data

uponLookup = {v: k for k, v in gg_rev_script_parser.uponLookup.items()}
slotLookup = {v: k for k, v in gg_rev_script_parser.slotLookup.items()}
commandCounts = defaultdict(int)
commandCalls = defaultdict(list)
MODE = "<"
GAME = "bb"
output = ""
def decodeUpon(node):
    if node.name.replace("upon_","") in uponLookup:
        return uponLookup[node.name.replace("upon_","")]
    else:
        return int(node.name.replace("upon_",""))
def decodeVar(node):
    if isinstance(node, Num):
        return [0,node.n]
    elif node.id.replace("SLOT_","") in slotLookup:
        return [2,slotLookup[node.id.replace("SLOT_","")]]
    else:
        return [2,int(node.id.replace("SLOT_",""))]
def writeCommandByName(name,params):
    cmdData = commandDBLookup[name]
    writeCommandByID(cmdData["id"],params)
def writeCommandByID(id,params):
    global output
    cmdData = commandDB[str(id)]
    myParams = list(params)
    for index,oValue in enumerate(myParams):
        if isinstance(oValue,str):
            pass
        elif isinstance(oValue,int):
            pass
        elif isinstance(oValue,float):
            pass
        elif isinstance(oValue,Str):
            myParams[index] = oValue.s
        elif isinstance(oValue,Num):
            myParams[index] = oValue.n
        elif isinstance(oValue,Name):
            myParams[index] = int(named_value_lookup.value_for_name(commandDB[str(id)]["name"], oValue.id))
        else:
            raise Exception("Unknown Type" + str(type(oValue)))
    output.write(struct.pack(MODE+"I",id))
    if cmdData.get('format', "notempty") == "":
        return
    if cmdData.get('size', 5) == 4:
        return
    if "format" in cmdData:
        output.write(struct.pack(MODE+cmdData["format"],*myParams))
    else:
        output.write(myParams[0].decode('hex'))

class Rebuilder(astor.ExplicitNodeVisitor):
    def visit_Module(self,node):
        global output
        global root
        root = node
        stateCount = 0
        output.write(struct.pack(MODE+"I",stateCount))
        for function in node.body:
            if type(function) != FunctionDef:
                raise Exception("Root level elements must be functions")
            if function.name[:2] == '__' and function.name[2].isdigit():
                function.name = function.name[2:]
            if function.decorator_list[0].id != "State":
                continue
            function._index = stateCount
            stateCount += 1
            output.write(struct.pack(MODE+"32sI",function.name,0xFADEF00D))
        node._dataStart = output.tell()
        output.seek(0)
        output.write(struct.pack(MODE+"I",stateCount))
        for childNode in node.body:
            self.visit_RootFunctionDef(childNode)
    def visit_RootFunctionDef(self,node):
        global output,root
        output.seek(0,2)

        if len(node.decorator_list) == 1:
            if node.name[:2] == '__' and function.name[2].isdigit():
                node.name = node.name[2:]
            if node.decorator_list[0].id == "State":
                #Write offset into state table
                startOffset = output.tell()-root._dataStart
                output.seek(4+36*node._index+32)
                output.write(struct.pack(MODE+"I",startOffset))
                output.seek(0,2)
                writeCommandByName("startState",[node.name])
                self.visit_body(node.body)
                writeCommandByName("endState",[])
            else:
                writeCommandByName("startSubroutine",[node.name])
                self.visit_body(node.body)
                writeCommandByName("endSubroutine",[])
        else:
            raise Exception("haven't implemented this")
    def visit_Pass(self,node):
        pass
    def visit_Call(self,node):
        # We have a function call. Is it a named function or is it UnknownXXXXX
        if "Unknown" in node.func.id:
            cmdId = int(node.func.id.replace("Unknown",""))
        elif node.func.id in commandDBLookup:
            cmdId = commandDBLookup[node.func.id]["id"]
        else:
            raise Exception("Unknown Command "+node.func.id)
        writeCommandByID(cmdId,node.args)
    def visit_FunctionDef(self,node):
        if "upon" not in node.name:
            raise Exception("inner functions are used for upon handlers only")
        writeCommandByName("upon",[decodeUpon(node)])
        self.visit_body(node.body)
        writeCommandByName("endUpon",[])
    def visit_If(self,node):
        if isinstance(node.test,Name):
            #This is if(SLOT) we need to find out slot index and write it as param of if
            writeCommandByName("if",decodeVar(node.test))
            self.visit_body(node.body)
            writeCommandByName("endIf",[])
            if len(node.orelse) > 0:
                writeCommandByName("else",[])
                self.visit_body(node.orelse)
                writeCommandByName("endElse",[])
        elif isinstance(node.test,UnaryOp) and isinstance(node.test.operand,Name):
            #This is if(SLOT) we need to find out slot index and write it as param of if
            writeCommandByName("ifNot",decodeVar(node.test.operand))
            self.visit_body(node.body)
            writeCommandByName("endIf",[])
            if len(node.orelse) > 0:
                writeCommandByName("else",[])
                self.visit_body(node.orelse)
                writeCommandByName("endElse",[])
        elif (isinstance(node.test,Call) or isinstance(node.test,Compare)):
            self.visit(node.test)
            if(isinstance(node.test,Call)):
                writeCommandByName("if",[2,0])
            self.visit_body(node.body)
            writeCommandByName("endIf",[])
            if len(node.orelse) > 0:
                writeCommandByName("else",[])
                self.visit_body(node.orelse)
                writeCommandByName("endElse",[])
        elif isinstance(node.test,UnaryOp) and (isinstance(node.test.operand,Call) or isinstance(node.test.operand,Compare)):
            self.visit(node.test.operand)
            if(isinstance(node.test.operand,Call)):
                writeCommandByName("ifNot",[2,0])
            self.visit_body(node.body)
            writeCommandByName("endIf",[])
            if len(node.orelse) > 0:
                writeCommandByName("else",[])
                self.visit_body(node.orelse)
                writeCommandByName("endElse",[])
        else:
            print "UNHANDLED IF",astor.dump(node)
        #If(SLOT)
        #If(Expr)
        #If(UnaryOp(Expr))
    def visit_Assign(self,node):
        if isinstance(node.value,BinOp):
            params = []
            if isinstance(node.value.op,Add):
                params.append(0)
            elif isinstance(node.value.op,Sub):
                params.append(1)
            elif isinstance(node.value.op,Mult):
                params.append(2)
            elif isinstance(node.value.op,Div):
                params.append(3)
            else:
                print "UNIMPLEMENTED BINOP",astor.dump(node)
                raise Exception("Unknown Operation!")
            writeCommandByName("ModifyVar_",params+decodeVar(node.targets[0])+decodeVar(node.value.right))
        else:
            writeCommandByName("StoreValue",decodeVar(node.targets[0])+decodeVar(node.value))
    def visit_Compare(self,node):
        params = []
        if isinstance(node.ops[0],Eq):
            params.append(9)
        elif isinstance(node.ops[0],Gt):
            params.append(10)
        elif isinstance(node.ops[0],Lt):
            params.append(11)
        elif isinstance(node.ops[0],GtE):
            params.append(12)
        elif isinstance(node.ops[0],LtE):
            params.append(13)
        elif isinstance(node.ops[0],NotEq):
            params.append(15)
        else:
            print "UNIMPLEMENTED BINOP",astor.dump(node)
            raise Exception("Unknown Compare")
        writeCommandByName("op",params+decodeVar(node.left)+decodeVar(node.comparators[0]))
    def visit_body(self,nodebody):
        try:
            for childNode in nodebody:
                self.visit(childNode)
        except AttributeError as e:
            print e,astor.dump(childNode)
    def visit_Expr(self,node):
        self.visit(node.value)
    def generic_visit(self, node):
        print type(node).__name__


def rebuild_bbscript(sourceFilename,outFilename):
    global output
    sourceAST = astor.parsefile(sourceFilename)
    if(os.path.isfile(sourceFilename+".txt")):
        os.remove(sourceFilename+".txt")
    f = open(sourceFilename+".txt","w")
    f.write(astor.dump(sourceAST))
    f.close()
    output = open(outFilename,"wb")
    Rebuilder().visit(sourceAST)
    output.close()


if len(sys.argv) < 3:
    print "Usage:python gg_rev_script_rebuilder.py inputfile.py outputfile.ggscript"
    sys.exit(1)
basepath = os.path.dirname(os.path.realpath(sys.argv[0]))
sourcefn = os.path.join(basepath, sys.argv[1])
outfn = os.path.join(basepath, sys.argv[2])
rebuild_bbscript(sourcefn, outfn)
