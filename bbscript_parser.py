import os, struct, json, pac
from collections import defaultdict, OrderedDict
commandCounts = defaultdict(int)
commandCalls = defaultdict(list)


def sanitizer(command):
    def sanitize(s):
        if isinstance(s,str):
            s = "'{0}'".format(s.strip("\x00"))
        elif command and "hex" in commandDB[str(command)]:
            s = hex(s)
        return str(s).strip("\x00")
    return sanitize

def parse_bbscript_routine(f,end = -1):
    log,charName,j
    currentCMD = -1
    currentIndicator = "_PRE"
    currentFrame = 1
    currentIndent = 0
    while currentCMD != 1 and f.tell() != end:

        loc = f.tell()
        currentCMD, = struct.unpack("<I",f.read(4))
        if currentCMD in [4,6,15,14001]:
            if log: log.write("\n")
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
            cmdData = list(struct.unpack(dbData["format"],f.read(struct.calcsize(dbData["format"]))))
        commandCalls[currentCMD].append((characters[charName],currentIndicator,currentFrame,"{0}({1})".format(dbData["name"],",".join(map(sanitizer(currentCMD),cmdData)))))
        if currentCMD == 0:
            if log: log.write(indent+"@State()\n".format(loc))
            if log: log.write(indent+"def {0}():\n".format(cmdData[0].strip("\x00")))
            currentIndicator = cmdData[0].strip("\x00")
            currentContainer = [cmdData[0].strip("\x00")]
            j["States"].append(currentContainer)
        elif currentCMD == 8:
            if log: log.write(indent+"\n@Subroutine()\n".format(loc))
            if log: log.write(indent+"def {0}():\n".format(cmdData[0].strip("\x00")))
            currentIndicator = cmdData[0].strip("\x00")
            currentContainer = [cmdData[0].strip("\x00")]
            j["Subroutines"].append(currentContainer)
        elif currentCMD in [1,9]:
            pass
        else:
            if log: log.write(indent+"{0}({1})\n".format(dbData["name"],",".join(map(sanitizer(currentCMD),cmdData))))
            currentContainer.append([dbData["name"]] + map(sanitizer(currentCMD),cmdData))
        if currentCMD == 2:
            if log:
                log.seek(-1,1)
                log.write("#Frame {0}->{1}\n".format(currentFrame,currentFrame+cmdData[1]))
            currentFrame = currentFrame+cmdData[1]
        if currentCMD in [5,16,57,14002]:
            if log: log.write("\n")
        if currentCMD in [0,4,8,15,54,56,14001]:
            currentIndent += 1

def parse_bbscript(f,basename,filename,filesize):
    global commandDB,log,charName,j
    BASE = f.tell()
    log = None
    j = OrderedDict()
    j["Subroutines"] = []
    j["States"] = []
    outfilename = None
    if outfilename:
        log = open(outfilename,"w+b")
    charName = filename[-6:-4]
    if log: log.write("'''{0}'''\n".format(filename))
    FUNCTION_COUNT, = struct.unpack("<I",f.read(4))
    f.seek(BASE+4+0x20)
    initEnd, = struct.unpack("<I",f.read(4))
    initEnd = initEnd+4+0x24*FUNCTION_COUNT
    f.seek(BASE+4+0x24*(FUNCTION_COUNT))
    parse_bbscript_routine(f,initEnd)
    for i in range(0,FUNCTION_COUNT):
        f.seek(BASE+4+0x24*i)
        FUNCTION_NAME = f.read(0x20).split("\x00")[0]
        if log: log.write("\n#---------------{0} {1}/{2}\n".format(FUNCTION_NAME,i,FUNCTION_COUNT))
        FUNCTION_OFFSET, = struct.unpack("<I",f.read(4))
        f.seek(BASE+4+0x24*FUNCTION_COUNT+FUNCTION_OFFSET)
        parse_bbscript_routine(f)
#    log.seek(0)
#    data = log.read()
#    log.seek(0)
#    from pygments import highlight
#    from pygments.lexers import PythonLexer
#    from pygments.formatters import HtmlFormatter
#    log.write("<style type='text/css'>\n")
#    log.write(HtmlFormatter().get_style_defs('.highlight'))
#    log.write("</style>\n")
#    log.write(highlight(data, PythonLexer(), HtmlFormatter()))
    if log: log.close()
    return filename,j
#import glob
#for filename in glob.glob("output2/char_*/scr_*.bin"):
#    if "boss" in filename: continue
#    parse_bbscript(filename, "scr/"+os.path.basename(filename).replace("bin","py"))

#total = sum(commandCounts.values())
#tableCount = 0
#for k,v in sorted(commandCounts.items(),cmp=lambda x,y: cmp(-x[1],-y[1])):

#    print "{4:3} {3:8.4f} {0:10} {1:10} {2}".format(k,v,commandDB[str(k)],float(v)/total*100,tableCount)
#    tableCount += 1
#for k,v in sorted(commandCalls.items(),cmp=lambda x,y: cmp(x[0],y[0])):
#print "writing reports"
#for cmdId in commandCalls:
#    report = open("reports/"+str(cmdId)+".txt","w");
#    for thing in commandCalls[cmdId]:
#        report.write(str(thing)+"\n")
#    report.close()

#    for vv in v:
#        print v
