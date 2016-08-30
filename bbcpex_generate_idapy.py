import os, struct, json, pac
from collections import defaultdict, OrderedDict
f = open("ida.py","wb")
json_data=open("static_db/bb/commandDB.json").read()
commandDB = json.loads(json_data, object_pairs_hook=OrderedDict)
off = 0x007D86D8
off2 = 0x5C
for key,data in commandDB.items():
    if "name" in data:
        name = data["name"]
    else:
        name = "Unknown"+key
    f.write("#{0:X}\n".format(off2))
    f.write("MakeDword(0x{0:X})\n".format(off,name))
    f.write("MakeName(Dword(0x{0:X}),\"bbs_{1}\")\n".format(off,name))
    off += 4
    off2 += 4
f.close()
