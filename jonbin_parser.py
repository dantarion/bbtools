from collections import OrderedDict
import struct
def parse(f,basename,filename,filesize):
    BASE = f.tell()
    j = OrderedDict()
    j["Images"] = []

    f.read(4)
    imageCount, = struct.unpack("<H",f.read(2))
    for i in range(0,imageCount):
        j["Images"].append(f.read(32).split("\x00")[0])
    f.read(3)
    chunkCount,hurtboxCount,hitboxCount,unkboxCount,unk2BoxCount= struct.unpack("<Ihhhh",f.read(12))
    j["Unknown2"] = struct.unpack("<39H",f.read(39*2))
    j["Chunks"] = []
    for i in range(0,chunkCount):
        chunk = OrderedDict()
        chunk["SrcX"],chunk["SrcY"],chunk["SrcWidth"],chunk["SrcHeight"], \
        chunk["X"],chunk["Y"],chunk["Width"],chunk["Height"] = struct.unpack("<4f4f",f.read(4*8))
        chunk["Unknown"] = struct.unpack("<4I4I",f.read(4*8))
        chunk["Layer"], = struct.unpack("<I",f.read(4*1))
        chunk["Unknown2"] = struct.unpack("<3I",f.read(3*4))
        j["Chunks"].append(chunk)
    j["Hurtboxes"] = []
    for i in range(0,hurtboxCount):
        box = OrderedDict()
        box["ID"],box["X"],box["Y"],box["Width"],box["Height"] = struct.unpack("<I4f",f.read(20))
        j["Hurtboxes"].append(box)
    j["Hitboxes"] = []
    for i in range(0,hitboxCount):
        box = OrderedDict()
        box["ID"],box["X"],box["Y"],box["Width"],box["Height"] = struct.unpack("<I4f",f.read(20))
        j["Hitboxes"].append(box)
    j["BoxType3"] = []
    for i in range(unkboxCount):
            box = OrderedDict()
            box["ID"],box["X"],box["Y"],box["Width"],box["Height"] = struct.unpack("<I4f",f.read(20))
            j["BoxType3"].append(box)
    return filename,j
