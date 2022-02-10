from MLP import MLP
from PipeLine import PipeLine
from ResultWritter import ResultWritter
import time
import torch
import torch.nn as nn


def runDeepGraphlet(deviceID):
    
    time_start = time.time()
    nowTime = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    resultWritter = ResultWritter("../result/" + nowTime)
    
    for dataName in ["artist_edges"]:
        args = {}
        args['numLayer'] = 3
        args['mlpPos'] = [0, 1, 2]
        args['nclasses'] = [2, 6, 21]

        args['baseModel'] = "DeepGraphlet"
        args['useKTupleFeature'] = True
        args['numIterator'] = 200
        args['learningRate'] = 0.001
        args['weightDecay'] = 0
        args['useDropout'] = True
        args['keepProb'] = 0.5
        args['useBatchNorm'] = True
        args['aggregator'] = "mean"
        args['loss'] = "kl"

        
        model = PipeLine(["../data/" + dataName], resultWritter = resultWritter, args = args, deviceID = deviceID, writeInfo = deviceID)
        model.load_args(args)
        model.train_graph(modelPath = "../model/" + dataName)
        valData = ["../data/" + dataName + ".edges"]
        model.load_infer_data(valData)
        # model = PipeLine(["../data/" + dataName],resultWritter = resultWritter, args = args, deviceID = deviceID, writeInfo = deviceID)
        model.LoadModel(modelPath = "../model/" + dataName)
        model.inferRealGraph(needLabel = True)
        time_end = time.time()
        print("time cost",time_end - time_start,'s')
        # resultWritter.writeResult('summary.txt', "time cost" + str(time_end - time_start) + 's')


if __name__ == '__main__':
    runDeepGraphlet(1)