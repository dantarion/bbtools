import os, struct, json, pac,astor
from ast import *
from collections import defaultdict, OrderedDict
import bbcpex_script_parser
json_data=open("static_db/bb/commandDB.json").read()
commandDB = json.loads(json_data)

json_data=open("static_db/bb/characters.json").read()
characters = json.loads(json_data)
commandDBLookup = {}
bbcpex_script_parser.commandDB = commandDB
bbcpex_script_parser.characters = characters
for key,data in commandDB.items():
    data["id"] = int(key)
    if "name" in data:
        commandDBLookup[data["name"]] = data
    else:
        commandDBLookup["Unknown"+key] = data

commandCounts = defaultdict(int)
commandCalls = defaultdict(list)
MODE = "<"
GAME = "bb"
output = ""
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
        else:
            raise AttributeError("Unknown Type" + str(type(oValue)))
    output.write(struct.pack(MODE+"I",id))
    if "format" in cmdData:
        output.write(struct.pack(MODE+cmdData["format"],*myParams))
    else:
        output.write(myParams[0].decode('hex'))

class Rebuilder(astor.ExplicitNodeVisitor):
    pass
    def visit_Module(self,node):
        global output
        global root
        root = node
        stateCount = 0
        output.write(struct.pack(MODE+"I",stateCount))
        for function in node.body:
            if type(function) != FunctionDef:
                raise Exception("Root level elements must be functions")
            if function.decorator_list[0].id != "State":
                continue
            function._index = stateCount
            stateCount += 1
            output.write(struct.pack(MODE+"32sI",function.name,0xFADEF00D))
        node._dataStart = output.tell()-4
        output.seek(0)
        output.write(struct.pack(MODE+"I",stateCount))
        for childNode in node.body:
            self.visit_RootFunctionDef(childNode)
    def visit_RootFunctionDef(self,node):
        global output,root
        output.seek(0,2)
        if len(node.decorator_list) == 1:
            if node.decorator_list[0].id == "State":
                #Write offset into state table
                startOffset = output.tell()-root._dataStart
                output.seek(4+36*node._index+32)
                output.write(struct.pack(MODE+"I",startOffset))
                output.seek(0,2)
                writeCommandByName("startState",[node.name])
                writeCommandByName("loopRest",[])
                try:
                    for childNode in node.body:
                        NodeVisitor.generic_visit(self, childNode)
                except AttributeError as e:
                    print e
                writeCommandByName("endState",[])
            else:
                writeCommandByName("startSubroutine",[node.name])
                writeCommandByName("loopRest",[])
                try:
                    for childNode in node.body:
                        NodeVisitor.generic_visit(self, childNode)
                except AttributeError as e:
                    print e
                writeCommandByName("endSubroutine",[])
        else:
            raise Exception("haven't implemented this")
    def visit_Call(self,node):
        # We have a function call. Is it a named function or is it UnknownXXXXX
        if "Unknown" in node.func.id:
            cmdId = int(node.func.id.replace("Unknown",""))
        else:
            cmdId = commandDBLookup[node.func.id]["id"]
        if not cmdId:
            raise Exception("Unknown Command")
        writeCommandByID(cmdId,node.args)
    def visit_Name(self,node):
        print astor.dump(node)


    def generic_visit(self, node):
        print type(node).__name__


def rebuild_bbscript(sourceFilename,outFilename):
    global output
    sourceAST = astor.parsefile(sourceFilename)
    f = open(outFilename+".txt","w")
    f.write(astor.dump(sourceAST))
    f.close()
    output = open(outFilename,"wb")
    Rebuilder().visit(sourceAST)
    output.close()
    output = open(outFilename,"rb")
    output.seek(0,2)
    filesize = output.tell()
    output.seek(0)
    bbcpex_script_parser.parse_bbscript(output,"","rebuild_kk",filesize)
    output.close()



rebuild_bbscript("db/bbcpex/scr_kk.bin.py","test_rebuild/rebuilt_kk.bin")
