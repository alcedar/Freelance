from os import listdir
from os.path import isfile, join
onlyfiles = [ f for f in listdir("./") if isfile(join("./",f)) ]
for filename in onlyfiles:
    if filename.endswith(".txt"):
        print filename
        content = open(filename, "r").readlines()
        content.insert(0, filename + "\n")
        output = open(filename, "w")
        output.write(''.join(content))
        output.close()