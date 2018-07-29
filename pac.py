import os,struct,glob,zlib,subprocess
OUT_PATH = "bbcf2/"
IN_PATH = r"G:\SteamLibrary\steamapps\common\BlazBlue Centralfiction\data\Char"
MODE = "<"
def find_active(f,basename,filename,filesize):
    f.seek(0x2F,1)
    if struct.unpack("B", f.read(1))[0] != 0:
        print filename[:-7]
def dump_pac(f,basename,filename,filesize):
    if not os.path.isdir(OUT_PATH+basename+".extracted"):
        os.makedirs(OUT_PATH+basename+".extracted")
    else:
        pass
    outFilename = os.path.join(OUT_PATH+basename+".extracted",filename)
    if os.path.isfile(outFilename):
            return
    print filename
    out = open(outFilename,"wb")
    out.write(f.read(filesize))
    out.close()
def iterpac(filename,func):
    global MODE
    basename = os.path.split(filename)[1]
    f = open(filename,"rb")
    BASE = 0
    if f.read(4) != "FPAC":
        f.seek(0x48)
        #XRD PAC
        BASE = 0x48
        MODE = ">"
        if f.read(4) != "FPAC":
            print "\t","Not a valid .pac file"
            return
    DATA_START,TOTAL_SIZE,FILE_COUNT = struct.unpack(MODE+ "3I",f.read(12))
    if FILE_COUNT == 0:
        return
    UNK01,STRING_SIZE,UNK03,UNK04 = struct.unpack(MODE+ "4I",f.read(16))
    ENTRY_SIZE = (DATA_START-0x20)/FILE_COUNT
    #STRING_SIZE = (STRING_SIZE + 15) & ~15

    for i in range(0,FILE_COUNT):
        f.seek(BASE+0x20+i*(ENTRY_SIZE)+0x10)
        FILE_NAME,FILE_ID,FILE_OFFSET,FILE_SIZE,UNK = struct.unpack(MODE+str(STRING_SIZE)+"s4I",f.read(0x10+STRING_SIZE))
        FILE_NAME = FILE_NAME.split("\x00")[0]
        f.seek(BASE+DATA_START+FILE_OFFSET)
        yield func(f,basename,FILE_NAME,FILE_SIZE)


#for filename in glob.glob("disc/P4AU/char/char_kk_*.pac"):
if __name__ == "__main__":
    for filename in glob.glob(os.path.join(IN_PATH, 'char_*_pal.pac')):
        print filename
        for thing in iterpac(filename,dump_pac):
            print thing
    print "done"
