'''
This script takes the PC version of
Blazblue Chronophantasma Extend and grabs the character files we need, decrypts them, and decompresses them

Change TARGET_FOLDER and place ggxrd_decrypter.exe in this folder and run this script.

https://www.reddit.com/r/Guiltygear/comments/3w7set/xrd_pc_upk_decrypter/

'''
import os, struct,zlib
import subprocess
TARGET_FOLDER = "M:\\SteamLibrary\\SteamApps\\common\\BlazBlue Chronophantasma Extend\\data\\char_e_cp\\"
for root,dirs,files in os.walk(TARGET_FOLDER):
    for filename in files:
        print os.path.join(root,filename)
        subprocess.call(["ggxrd_decrypter.exe",os.path.join(root,filename)],shell=True)
        if os.path.isfile("input/bbcp/"+filename):
            os.remove("input/bbcp/"+filename)
        os.rename(os.path.join(root,filename)+".decrypted","input/bbcp/"+filename)
        f = open("input/bbcp/"+filename,"r+b")
        f.seek(0x10)
        data = zlib.decompress(f.read())
        f.seek(0)
        f.write(data)
        f.close()
