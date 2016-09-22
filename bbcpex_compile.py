import bbcpex_script_parser,jonbin_parser,pac
import os,glob,json,struct
from collections import OrderedDict

def parse_hipoffset(f,basename,filename,filesize):
    if f.read(4) != "HIP\x00":
        raise Exception("This isn't a HIP file")
    DATA = struct.unpack("<3I4I4I4I",f.read(0x3C))
    return filename,[DATA[9],DATA[10]]


json_data=open("static_db/bb/commandDB.json").read()
commandDB = json.loads(json_data)

json_data=open("static_db/bb/characters.json").read()
characters = json.loads(json_data)


bbcpex_script_parser.commandDB = commandDB
bbcpex_script_parser.characters = characters
if __name__ == "__main__":
    for game in ["bbcsex","bbcp","bbcpex"]:
        for character in characters:
            if character != "kk": continue
            scr_filename = "input/{0}/char_{1}_scr.pac".format(game,character);
            if not os.path.isfile(scr_filename): continue
            print game,character


            compiledData = OrderedDict()

            #Dantarion: Get all the bbscript info and store it in here
            compiledData["scr"] = []
            for filename,data in pac.iterpac(scr_filename,bbcpex_script_parser.parse_bbscript):
                compiledData["scr"].append({"filename":filename, "data":data})
            '''
            #Dantarion: This data is discarded by exah3pac but we need it for arranging sprites later!
            img_filename = "input/bbcpex/char_{0}_img.pac".format(character);
            compiledData["hipoffset"] = {}
            for filename,data in pac.iterpac(img_filename,parse_hipoffset):
                compiledData["hipoffset"][filename] = data
            vri_filename = "input/bbcpex/char_{0}_vri.pac".format(character);
            for filename,data in pac.iterpac(vri_filename,parse_hipoffset):
                compiledData["hipoffset"][filename] = data
            #Dantarion: Sprite Chunk Placement, Hit and Hurt boxes
            if game != "bbcsex":
                img_filename = "input/bbcpex/char_{0}_col.pac".format(character);
            else:
                img_filename = "input/bbcsex/char_{0}_col.pac".format(character);
            compiledData["col"] = OrderedDict()
            for filename,data in pac.iterpac(img_filename,jonbin_parser.parse):
                compiledData["col"][filename] = data
            '''
            #This creates a single monolithic json file with all data needed for boxdox.bb
            outJson = open("db/{0}/{1}.json".format(game,character),"w")
            outJson.write(json.dumps(compiledData,encoding='cp1252'))
            outJson.close()
'''
for cmdId in bbcpex_script_parser.commandCalls:
    module = (cmdId / 100) * 100
    if not os.path.isdir("reports/{0}/".format(module)):
        os.makedirs("reports/{0}/".format(module))
    report = open("reports/{0}/{1}.txt".format(module,cmdId),"w");
    for thing in bbcpex_script_parser.commandCalls[cmdId]:
        report.write("{0:15s} {1:15s} {2} {3}\n".format(*thing))
    report.close()
'''
