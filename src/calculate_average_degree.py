import os
def get_edge_num(filePath):
    f = open(filePath)
    line = f.readline()
    strN, strM = line.strip('\n').split(' ')
    return int(strN), int(strM.split('.')[0])

def trainVal(synDir):
    precent = 10
    filePath = []
    valPath = []
    totN, totM = get_edge_num(synDir[0] + '.edges')
    sumN = 0
    sumM = 0
    for path in synDir:
        filenames = os.listdir(path)
        filenames = [(path + "/" + name) for name in filenames]
        fileNames = []
        for name in filenames:
            if name.split('.')[-1] == "edges":
                N, M = get_edge_num(name)
                sumN += N
                sumM += M
    return totN, totM, sumN, sumM
