'''
This script gets files from a extracted Revelator PS3 patch PKG and extracts
certain packages to input/gg_revelator

extract.exe is from
http://www.gildor.org/downloads
Unreal Package Extractor

'''
import os, struct,zlib
import subprocess
TARGET_FOLDER = "X:\\PS3\\Revelator\\pkg\\UP1024-BLUS31588_00-GGXRDREVUS000104-A0104-V0100-PE\\BLUS31588\\USRDIR\\PATCH\\REDGAME\\COOKEDPS3\\"
for root,dirs,files in os.walk(TARGET_FOLDER):
    for filename in files:
        if "_DAT_" not in filename:
            continue
        #print os.path.join(root,filename)
        print filename
        subprocess.call(["extract.exe","-out=input/gg_revelator/","-extract",os.path.join(root,filename)],shell=True)
