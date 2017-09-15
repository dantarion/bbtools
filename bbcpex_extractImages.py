'''
This script takes files extracted by batchDecryptDecompressExtract.py and extracts .pac files containing .hip files into images.
You need to put exah3pac.exe in this folder.

http://asmodean.reverse.net/pages/exah3pac.html

'''
import os, struct,zlib
import subprocess
TARGET_FOLDER = "input/bbcf2/"
for root,dirs,files in os.walk(TARGET_FOLDER):
    for filename in files:
        if "_img." not in filename:
            continue
        print os.path.join(root,filename)
        subprocess.call(["exah3pac.exe",os.path.join(root,filename)],shell=True)
