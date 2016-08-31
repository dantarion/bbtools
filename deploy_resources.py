import os,subprocess,gzip,shutil

for root,dirs,files in os.walk("db/"):
    for fname in files:
        if ".py" not in fname and ".json" not in fname: continue
        with open(os.path.join(root,fname), 'rb') as f_in, gzip.open('tmp.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        params = ["aws","s3","cp","tmp.gz","s3://boxdox-bb.dantarion.com/"+os.path.join(root,fname),"--content-type", "text/plain", "--content-encoding", "gzip"]
        s = " ".join(params)
        subprocess.call(s,shell=True)
