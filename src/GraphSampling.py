from GenerateLabel import GenerateLabel
import queue
from utils import split_between_last_char, saveEdgeList, saveSet, readEdgeList
import os
import time

def sampling(nodeList, adj, expectedNodeNum):
    sampledNodeList = set()
    while len(sampledNodeList) < expectedNodeNum:
        q = queue.Queue()
        for node in nodeList:
            q.put(node)
            sampledNodeList.add(node)
            nodeList.remove(node)
            break
#         print(len(sampledNodeList))
        while q.empty() == False:
            u = q.get()
            for v in adj[u]:
                if len(sampledNodeList) >= expectedNodeNum:
                    break
                if v in nodeList:
                    sampledNodeList.add(v)
                    nodeList.remove(v)
                    q.put(v)
            if len(sampledNodeList) >= expectedNodeNum:
                break
    sampledEdgeList = []
    for u in sampledNodeList:
        for v in adj[u]:
            if v in sampledNodeList:
                sampledEdgeList.append([u, v])
    return sampledNodeList, sampledEdgeList

def edgeList2adj(n, edgeList):
    adj = []
    for i in range(n):
        adj.append([])
    for edge in edgeList:
        u, v = edge
        adj[u].append(v)
        adj[v].append(u)
    return adj

def partition(filePath, splitDen, splitNum):
    n, m, edgeList = readEdgeList(filePath)
    print("--------------------------------------------------------------------------------------------")
    print(n, m)
    prePath, fileName = split_between_last_char(filePath, '/')
    prefix, suffix = split_between_last_char(fileName, '.')
    savePath = prePath + '/' + prefix
    if os.path.exists(savePath):
        return
        # print(savePath)
        # os.system('rm -rf ' + savePath)
    os.system('mkdir ' + savePath)
    print(prePath, fileName)
    print(prefix, suffix)
    print(savePath)
    nodeList = set()
    for i in range(n):
        nodeList.add(i)
    expectedNodeNum = len(nodeList) / splitDen
    adj = edgeList2adj(n, edgeList)
    for i in range(splitNum):
        print(len(nodeList))
        sampledNodeList, sampledEdgeList = sampling(nodeList, adj, expectedNodeNum)
        print(len(nodeList))
        saveEdgeList(savePath + '/' + str(i) + '.edge', sampledEdgeList)
        print('node|edgeList length', len(sampledNodeList), len(sampledEdgeList))
        GenerateLabel(savePath + '/' + str(i) + '.edge')
        print('nodeList', len(nodeList))

    saveSet(savePath + '/' + 'nonSampled.nodes', nodeList)

if __name__ == '__main__':
    time_start = time.time()
    filePath = "../data/artist_edges.edges"
    partition(filePath, 30, 15)
    time_end = time.time()
    print("end: time cost" + str(time_end - time_start) + "s")
    