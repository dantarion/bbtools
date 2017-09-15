from collections import OrderedDict
import struct
GAME = "bbcp"
MODE = "<"
def parse(f,basename,filename,filesize):
    global GAME
    BASE = f.tell()
    j = OrderedDict()
    j["Images"] = []

    f.read(4)
    if GAME == "bbcp":
        imageCount, = struct.unpack(MODE+"H",f.read(2))
    else:
        imageCount, = struct.unpack(MODE+"I",f.read(4))
    for i in range(0,imageCount):
        j["Images"].append(f.read(32).split("\x00")[0])

    if GAME == "bbcp":
        f.read(3)
        chunkCount,hurtboxCount,hitboxCount,unkboxCount,unk2BoxCount= struct.unpack(MODE+"Ihhhh",f.read(12))
        j["Unknown2"] = struct.unpack(MODE+"39H",f.read(39*2))
        j["Chunks"] = []

        for i in range(0,chunkCount):
            chunk = OrderedDict()
            chunk["SrcX"],chunk["SrcY"],chunk["SrcWidth"],chunk["SrcHeight"], \
            chunk["X"],chunk["Y"],chunk["Width"],chunk["Height"] = struct.unpack(MODE+"4f4f",f.read(4*8))
            chunk["Unknown"] = struct.unpack(MODE+"4I4I",f.read(4*8))
            chunk["Layer"], = struct.unpack(MODE+"I",f.read(4*1))
            chunk["Unknown2"] = struct.unpack(MODE+"3I",f.read(3*4))
            j["Chunks"].append(chunk)
    elif GAME == "bbcf":
        f.read(8)
        chunkCount,unk,hurtboxCount,hitboxCount,unkboxCount,unk2BoxCount= struct.unpack(MODE+"IIIIII",f.read(24))

        j["Unknown2"] = struct.unpack(MODE+"52H",f.read(52*2))
        j["Chunks"] = []
        for i in range(0,chunkCount):
            chunk = OrderedDict()
            chunk["SrcX"],chunk["SrcY"],chunk["SrcWidth"],chunk["SrcHeight"], \
            chunk["X"],chunk["Y"],chunk["Width"],chunk["Height"] = struct.unpack(MODE+"4f4f",f.read(4*8))
            chunk["Unknown"] = struct.unpack(MODE+"4I4I",f.read(4*8))
            chunk["Layer"], = struct.unpack(MODE+"I",f.read(4*1))
            chunk["Unknown2"] = struct.unpack(MODE+"3I",f.read(3*4))
            j["Chunks"].append(chunk)

    else:
        f.seek(BASE+0x38)
        hurtboxCount,hitboxCount,unkboxCount,unk2BoxCount= struct.unpack(MODE+"4I",f.read(0x10))
        f.seek(BASE+0x100)


    j["Hurtboxes"] = []
    for i in range(0,hurtboxCount):
        box = OrderedDict()
        box["ID"],box["X"],box["Y"],box["Width"],box["Height"] = struct.unpack(MODE+"I4f",f.read(20))
        j["Hurtboxes"].append(box)
    j["Hitboxes"] = []
    for i in range(0,hitboxCount):
        box = OrderedDict()
        box["ID"],box["X"],box["Y"],box["Width"],box["Height"] = struct.unpack(MODE+"I4f",f.read(20))
        j["Hitboxes"].append(box)
    j["BoxType3"] = []
    for i in range(unkboxCount):
            box = OrderedDict()
            box["ID"],box["X"],box["Y"],box["Width"],box["Height"] = struct.unpack(MODE+"I4f",f.read(20))
            j["BoxType3"].append(box)
    return filename,j
