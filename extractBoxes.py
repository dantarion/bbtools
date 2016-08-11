import os,struct,glob,json,sys
from p4a import iterpac
from PIL import Image,ImageDraw,ImageFilter
unknowndict = {}
def dumpBoxes(f,basename,filename,filesize):
    BASE = f.tell()
    print filename
    sig = f.read(4)
    if sig != "JONB":
        return
    HEADER = struct.unpack(">h32s",f.read(40))
    print HEADER
    f.seek(BASE+8+0x20*HEADER[0]+4)
    srcImageName = HEADER[1].split('\x00')[0].replace(".bmp",".png")
    
    DATA = struct.unpack(">12I",f.read(12*4))
    DATA2 = struct.unpack(">21I",f.read(0x54))
    print "\t",HEADER
    print "\t",srcImageName
    print "\t",DATA
    print "\t",DATA2
    if not os.path.isfile("img/"+srcImageName[0:2]+"/"+srcImageName):
        return
        pass
    src = Image.open("img/"+srcImageName[0:2]+"/"+srcImageName)
    src = src.convert("RGBA")
    #src.load()
    dst = ""
    import pickle
    
    p = pickle.load(open("img/"+srcImageName[0:2]+"/"+srcImageName+".pick","rb"))
    CANVAS_HEIGHT = 1024
    CANVAS_WIDTH = 1024
    dst = Image.new("RGB", (int(CANVAS_WIDTH), int(CANVAS_HEIGHT)),src.info["transparency"])
    XMin =  1000000000000
    XMax = -1000000000000
    YMin =  1000000000000
    YMax = -1000000000000
    for i in range(0, DATA[1]):
        
        SrcX, SrcY, SrcWidth, SrcHeight, X, Y, Width, Height = struct.unpack(">8f",f.read(0x20))

        
        #XMin = min(XMin,int(SrcX)-p[9])
        #XMax = max(XMax,int(SrcWidth)-p[9]-SrcX)
        #YMin = min(YMin,int(SrcY)-p[10])
        #YMax = max(YMax,-SrcY+int(SrcHeight)-p[10])
        crop = src.copy().crop((int(SrcX)-p[9], int(SrcY)-p[10],int(SrcWidth)-p[9], int(SrcHeight)-p[10]))
        

        dst.paste(crop,(int(X)+512, int(Y)+512),mask=crop)
        #print "\t\t",SrcX, SrcY, SrcWidth, SrcHeight, X, Y, Width, Height
        #print "\t\t","pick",p[3],p[4]
        struct.unpack(">8f",f.read(0x20))
        Layer = struct.unpack(">i",f.read(0x4))
        #print "\t\t",Layer
        struct.unpack(">3i",f.read(0xC))
    
    #dst = dst.filter(ImageFilter.BLUR)
    
    draw = ImageDraw.Draw(dst)

 
    for i in range(0, DATA[2]):
        ID, X, Y, Width, Height = struct.unpack("<I4f",f.read(0x14))
        XMin = min(XMin,X)
        XMax = max(XMax,X+Width)
        YMin = min(YMin,Y)
        YMax = max(YMax,Y+Height)
        #print "\t\tBox->",ID, X, Y, Width, Height
        draw.rectangle((X+CANVAS_WIDTH/2,Y+CANVAS_HEIGHT/2,X+Width+CANVAS_WIDTH/2,Y+Height+CANVAS_HEIGHT/2),outline=(255,0,0))
    for i in range(0, DATA[3]):
        ID, X, Y, Width, Height = struct.unpack("<I4f",f.read(0x14))
        XMin = min(XMin,X)
        XMax = max(XMax,X+Width)
        YMin = min(YMin,Y)
        YMax = max(YMax,Y+Height)
        #print "\t\tBox->",ID, X, Y, Width, Height
        draw.rectangle((X+CANVAS_WIDTH/2,Y+CANVAS_HEIGHT/2,X+Width+CANVAS_WIDTH/2,Y+Height+CANVAS_HEIGHT/2),outline=(255,255,0))
    for i in range(0, DATA[4]):
        ID, X, Y, Width, Height = struct.unpack("<I4f",f.read(0x14))
        XMin = min(XMin,X)
        XMax = max(XMax,X+Width)
        YMin = min(YMin,Y)
        YMax = max(YMax,Y+Height)
        #print "\t\tBox->",ID, X, Y, Width, Height
        draw.rectangle((X+CANVAS_WIDTH/2,Y+CANVAS_HEIGHT/2,X+Width+CANVAS_WIDTH/2,Y+Height+CANVAS_HEIGHT/2),outline=(255,0,0))
    for i in range(0, DATA[5]):
        ID, X, Y, Width, Height = struct.unpack("<I4f",f.read(0x14))
        XMin = min(XMin,X)
        XMax = max(XMax,X+Width)
        YMin = min(YMin,Y)
        YMax = max(YMax,Y+Height)
        #print "\t\tBox->",ID, X, Y, Width, Height
        draw.rectangle((X+CANVAS_WIDTH/2,Y+CANVAS_HEIGHT/2,X+Width+CANVAS_WIDTH/2,Y+Height+CANVAS_HEIGHT/2),outline=(255,0,255))
    if not os.path.isdir("boxes/"+srcImageName[0:2]):
        os.makedirs("boxes/"+srcImageName[0:2])
    try:
        print XMin,YMin, XMax, YMax
        dst =  dst.crop(((int(XMin+CANVAS_WIDTH/2)-64,int(YMin+CANVAS_HEIGHT/2)-64,int(XMax+CANVAS_WIDTH/2)+64,int(YMax+CANVAS_HEIGHT/2)+64)))
        dst.save("boxes/"+srcImageName[0:2]+"/"+filename+".png",transparency=src.info["transparency"])
    except Exception:
        return
for filename in glob.glob("out/char_kk_col.pac"):
#for filename in glob.glob("C:/Users/Eric/Dropbox/Projects/SFxTConsole/SFxTConsole/bin/Debug/out/char_*_scr.pac"):

    iterpac(filename,dumpBoxes)
    

