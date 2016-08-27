import bbcpex_script_parser,jonbin_parser,pac
import os,glob,json,struct
from collections import OrderedDict

def parse_hipoffset(f,basename,filename,filesize):
    if f.read(4) != "HIP\x00":
        raise Exception("This isn't a HIP file")
    DATA = struct.unpack("<3I4I4I4I",f.read(0x3C))
    return filename,[DATA[9],DATA[10]]


json_data=open("static_db/gg_revelator/commandDB.json").read()
commandDB = json.loads(json_data)

json_data=open("static_db/gg_revelator/characters.json").read()
characters = json.loads(json_data)


bbcpex_script_parser.commandDB = commandDB
bbcpex_script_parser.characters = characters
bbcpex_script_parser.MODE = ">"
if __name__ == "__main__":
    for game,outputdir,srcdir in [["gg_revelator","gg_revelator_103","SF"],["gg_revelator","gg_revelator_102","20_SF"]]:
        for character in characters:
            scr_filename = "input/{0}/{1}_DAT_SF/{1}_dat/Script/BBS_{1}.REDAssetCharaScript".format(game,character,srcdir);
            scr_filename2 = "input/{0}/{1}_DAT_SF/{1}_dat/Script/BBS_{1}EF.REDAssetCharaScript".format(game,character,srcdir);
            if not os.path.isfile(scr_filename): continue
            print outputdir,character


            compiledData = OrderedDict()

            #Dantarion: Get all the bbscript info and store it in here
            compiledData["scr"] = []
            for _filename in [scr_filename,scr_filename2]:
                f = open(_filename,"rb")
                f.seek(0,2)
                filesize = f.tell()
                f.seek(0x48)
                filename, data = bbcpex_script_parser.parse_bbscript(f,"","char",filesize)
                compiledData["scr"].append({"filename":os.path.basename(_filename), "data":data})
            '''
            #Dantarion: This data is discarded by exah3pac but we need it for arranging sprites later!
            img_filename = "input/bbcpex/char_{0}_img.pac".format(character);
            compiledData["hipoffset"] = {}
            for filename,data in pac.iterpac(img_filename,parse_hipoffset):
                compiledData["hipoffset"][filename] = data
            vri_filename = "input/bbcpex/char_{0}_vri.pac".format(character);
            for filename,data in pac.iterpac(vri_filename,parse_hipoffset):
                compiledData["hipoffset"][filename] = data
            '''
            #Dantarion: Sprite Chunk Placement, Hit and Hurt boxes
            col_filename = "input/{0}/{1}_DAT_SF/{1}_dat/Collision/COL_{1}.REDAssetCollision".format(game,character,srcdir);

            compiledData["col"] = OrderedDict()
            jonbin_parser.GAME = "gg"
            for filename,data in pac.iterpac(col_filename,jonbin_parser.parse):
                compiledData["col"][filename] = data

            #This creates a single monolithic json file with all data needed for boxdox.bb
            outJson = open("db/{0}/{1}.json".format(outputdir,character),"w")
            outJson.write(json.dumps(compiledData,encoding='cp1252'))
            outJson.close()
