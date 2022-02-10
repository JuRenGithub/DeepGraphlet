import os
from utils import split_between_last_char
import time

def GenerateLabel(path):
    time_start = time.time()
    sanitize = "./orbit-counting/python/sanitize.py"
    orbit_counts = "./orbit-counting/wrappers/orbit_counts.py"
    outPath = "./orbit-counting/wrappers/"
    outName = "out.txt"
    prePath, fileName = split_between_last_char(path, '/')
    print(prePath, fileName)
    prefix, _ = split_between_last_char(fileName, '.')
    if os.path.exists(prePath + "/" + prefix + "." + "edges") == False:
        os.system('python ' + sanitize + " " + prePath + " " + fileName)
    suffix = 'edges'
    print(prefix, suffix)
    print('python3 ' + orbit_counts + " " + prePath + "/" + prefix + "." + suffix  + " 5 -c")
    if os.path.exists(prePath + "/" + prefix + "." + "out"):
        return
    os.system('python3 ' + orbit_counts + " " + prePath + "/" + prefix + "." + suffix  + " 5 -c")
    os.system("mv ./out.txt " + prefix + ".out")
    os.system("mv " + prefix + ".out " + prePath)
    time_end = time.time()
    print("generate label for " + path + " time cost: " + str(time_end - time_start) + "s")
    
if __name__ == '__main__': 
    time_start = time.time()
    GenerateLabel("../data/artist_edges.edges")
    time_end = time.time()
    print("time cost" + str(time_end - time_start) + "s")