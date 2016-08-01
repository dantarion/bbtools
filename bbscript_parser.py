import os, struct, json
json_data=open("commandDB.json").read()
commandDB = json.loads(json_data)
def sanitize(s):
    if isinstance(s,str):
        s = "'{0}'".format(s.strip("\x00"))
    return str(s).strip("\x00")

def parse_bbscript_routine(end = -1):
    global f,log
    currentCMD = -1
    while currentCMD != 1 and f.tell() != end:
        loc = f.tell()
        currentCMD, = struct.unpack("<I",f.read(4))
        if "format" not in commandDB[str(currentCMD)]:
            if log: log.write("\tUnknown_{0}('{1}')\n".format(currentCMD,f.read(commandDB[str(currentCMD)]["size"]-4).encode("hex")))
        else:
            dbData = commandDB[str(currentCMD)]
            if "name" not in dbData:
                dbData["name"] = "Unknown{0}".format(currentCMD)

            if "format" in dbData:
                cmdData = list(struct.unpack(dbData["format"],f.read(struct.calcsize(dbData["format"]))))
            if currentCMD == 0:
                if log: log.write("@State(0x{0:X})\n".format(loc))
                if log: log.write("def {0}():\n".format(cmdData[0].strip("\x00")))
            elif currentCMD == 8:
                if log: log.write("\n@Subroutine(0x{0:X})\n".format(loc))
                if log: log.write("def {0}():\n".format(cmdData[0].strip("\x00")))
            elif currentCMD in [1,9]:
                pass
            else:
                if log: log.write("\t{0}({1})\n".format(dbData["name"],",".join(map(sanitize,cmdData))))
        if currentCMD in [14002]:
            log.write("\n")

def parse_bbscript(filename, outfilename=None):
    global commandDB,f,log
    log = None
    if outfilename:
        log = open(outfilename,"w")
    print "'''{0}'''".format(filename)
    if log: log.write("'''{0}'''\n".format(filename))
    f = open(filename,"rb")
    FUNCTION_COUNT, = struct.unpack("<I",f.read(4))
    f.seek(4+0x20)
    initEnd, = struct.unpack("<I",f.read(4))
    initEnd = initEnd+4+0x24*FUNCTION_COUNT
    f.seek(4+0x24*(FUNCTION_COUNT))
    parse_bbscript_routine(initEnd)
    for i in range(0,FUNCTION_COUNT):
        f.seek(4+0x24*i)
        FUNCTION_NAME = f.read(0x20).split("\x00")[0]
        if log: log.write("\n#---------------{0} {1}/{2}\n".format(FUNCTION_NAME,i,FUNCTION_COUNT))
        FUNCTION_OFFSET, = struct.unpack("<I",f.read(4))
        f.seek(4+0x24*FUNCTION_COUNT+FUNCTION_OFFSET)
        parse_bbscript_routine()
parse_bbscript("output/char_rg_scr.pac.extracted/scr_rg.bin")
