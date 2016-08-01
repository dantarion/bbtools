import os, struct, json
json_data=open("commandDB.json").read()
commandDB = json.loads(json_data)
json_data=open("commandSizeDB.json").read()
commandSizeDB = json.loads(json_data)
def sanitize(s):
    if isinstance(s,str):
        s = "'{0}'".format(s.strip("\x00"))
    return str(s).strip("\x00")
def parse_bbscript_routine(end = -1):
    global f
    currentCMD = -1
    while currentCMD != 1 and f.tell() != end:
        loc = f.tell()
        currentCMD, = struct.unpack("<I",f.read(4))
        if "format" not in commandDB[str(currentCMD)]:
            print "\tUnknown_{0}('{1}')".format(currentCMD,f.read(commandSizeDB[str(currentCMD)]["size"]-4).encode("hex"))
        else:
            dbData = commandDB[str(currentCMD)]
            if "name" not in dbData:
                dbData["name"] = "Unknown{0}".format(currentCMD)

            if "format" in dbData:
                cmdData = list(struct.unpack(dbData["format"],f.read(struct.calcsize(dbData["format"]))))
            if currentCMD == 0:
                print "@State(0x{0:X})".format(loc)
                print "def {0}():".format(cmdData[0].strip("\x00"))
            elif currentCMD == 8:
                print "\n@Subroutine(0x{0:X})".format(loc)
                print "def {0}():".format(cmdData[0].strip("\x00"))
            elif currentCMD in [1,9]:
                pass
            else:
                print "\t{0}({1})".format(dbData["name"],",".join(map(sanitize,cmdData)))
        if currentCMD in [14002]:
            print


def parse_bbscript(filename):
    global commandDB,f
    print "'''{0}'''".format(filename)
    f = open(filename,"rb")
    FUNCTION_COUNT, = struct.unpack("<I",f.read(4))
    f.seek(4+0x20)
    initEnd, = struct.unpack("<I",f.read(4))
    initEnd = initEnd+4+0x24*FUNCTION_COUNT
    print hex(initEnd)
    f.seek(4+0x24*(FUNCTION_COUNT))
    parse_bbscript_routine(initEnd)
    for i in range(0,FUNCTION_COUNT):
        f.seek(4+0x24*i)

        FUNCTION_NAME = f.read(0x20).split("\x00")[0]
        print
        print "#---------------{0} {1}/{2}".format(FUNCTION_NAME,i,FUNCTION_COUNT)

        FUNCTION_OFFSET, = struct.unpack("<I",f.read(4))

        f.seek(4+0x24*FUNCTION_COUNT+FUNCTION_OFFSET)
        parse_bbscript_routine()







parse_bbscript("output/char_rg_scr.pac.extracted/scr_rg.bin")
