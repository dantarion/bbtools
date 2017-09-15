import os,struct,glob,gzip,zlib,json
from cStringIO import StringIO
from PIL import Image
for filename in glob.glob("bbcf2/char_ct_img.pac.extracted/*.hip"):
    outname = os.path.split(filename)[1].replace(".hip",".png")
    if not os.path.isdir("db/bbcf_200/img/"+outname[0:2]):
        os.makedirs("db/bbcf_200/img/"+outname[0:2])
    outfile = "db/bbcf_200/img/"+outname[0:2]+"/"+os.path.split(filename)[1].replace(".hip",".png")
    if os.path.isfile(outfile) or "dmy_camera.hip" in filename:
        continue
    f = open(filename,"rb")
    if f.read(4) != "HIP\x00":
        continue
    DATA = struct.unpack("<3I4I4I4I",f.read(0x3C))
    #print hex(DATA[6]&0xFFFF)
    #DATA2 = TOTAL_SIZE,PALLETE SIZE
    tmp = f.tell()
    f.seek(0,2)
    end = f.tell()
    f.seek(tmp)
    if DATA[2] == 0:
        print "WHAT IS THIS",filename

    else:

        PALLETE = []
        for i in range(0, 256):
            PALLETE.append(struct.unpack("4B",f.read(4))[::-1])
        #Get pallete
        tmp = os.path.split(filename.replace("_img","_pal"))

        palfile = os.path.join(tmp[0],tmp[-1][0:2]+"00_00.hpl")
        if not os.path.isfile(palfile):
           print "\t","couldn't find palette",palfile
           continue

        pal = open(palfile, "rb")
        pal.seek(0x20)
        PALLETE = []
        for i in range(0, 256):
            tmp = struct.unpack("4B",pal.read(4))
            PALLETE.append(list((tmp[0],tmp[1],tmp[2],tmp[3])[::-1]))
        PALLETE[0][0] = 0
        RAW_DATA = StringIO()
        while f.tell() < end:
            color = PALLETE[struct.unpack("B",f.read(1))[0]]
            counter = ord(f.read(1))


            RAW_DATA.write(struct.pack("4B",*color)*counter)
        img = Image.frombytes("RGBA",(DATA[7],DATA[8]),RAW_DATA.getvalue(),"raw","ARGB")
    #trueimg = Image.new("RGB", (DATA[3], DATA[4]),transparencycolor)
    #trueimg.paste(img,(DATA[3]-DATA[7],DATA[4]-DATA[8]))
    #img = trueimg
    print filename
    img.save(outfile,"png")
