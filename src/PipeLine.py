from GIN import GIN
from GCN import GCN
from DeepGraphlet import DeepGraphlet
from MSE import RMSE
import torch
import torch.optim as optim
import torch.nn as nn
import os
import numpy as np
import time
import pandas as pd
from KMLP import KMLP
from utils import printCurrentProcessMemory, printItemMemory, readEdgeList, split_between_last_char
import torch.nn.functional as F

device = torch.device('cuda')
cpu = torch.device('cpu')


class PipeLine:
    def __init__(self, dataPath, trainData=None, trainInfo=None, valData=None, valInfo=None, resultWritter="", args={},
                 deviceID=1, writeInfo=1):
        self.resultWritter = resultWritter
        self.args = {}

        # Set manually
        self.args['numLayer'] = 3
        self.args['nclasses'] = [2, 6, 21]
        self.args['mlpPos'] = [0, 1, 2]
        self.args['baseModel'] = "DeepGraphlet"
        self.args['numIterator'] = 200

        self.args['useRandomFeature'] = False
        self.args['useKTupleFeature'] = True

        self.args['useDropout'] = True
        self.args['useBatchNorm'] = True

        # Grid Search
        self.args['learningRate'] = 0.001
        self.args['weightDecay'] = 0
        self.args['keepProb'] = 0.5

        # nearly fixed parameters
        self.args['aggregator'] = "mean"
        self.args['activateFunc'] = "relu"
        self.args['hiddenDim'] = 128
        self.args['nodeFeatureDim'] = 29
        self.args['loss'] = "kl"
        for key, value in args.items():
            self.args[key] = value

        # if self.args['useRandomFeature'] == True:
        #     self.args['nodeFeatureDim'] = 29
        # if self.args['useKTupleFeature'] == True:
        #     self.args['nodeFeatureDim'] = 29

        print("featureDim: ", self.args['nodeFeatureDim'])

        self.writeInfo = str(writeInfo)

        if deviceID >= 0:
            torch.cuda.set_device(deviceID)

        self.trainData = {}
        self.trainInfo = {}
        self.valData = {}
        self.valInfo = {}
        if trainData != None:
            self.trainData = trainData
            self.trainInfo = trainInfo
            self.valData = valData
            self.valInfo = valInfo

        if self.args['loss'] == "kl":
            self.criterion = nn.KLDivLoss(reduction='batchmean')
        elif self.args['loss'] == "mse":
            self.criterion = RMSE()

        print('trainVal split')
        filePath, valPath = self.trainVal(dataPath)
        self.trainData, self.trainInfo = self.loadData(filePath)
        self.valData, self.valInfo = self.loadData(valPath)
        print(len(self.trainData), len(self.valData))

    def load_args(self, args):
        for key, value in args.items():
            self.args[key] = value
        if self.args['useKTupleFeature'] or self.args['useRandomFeature']:
            self.args['nodeFeatureDim'] = 29
        else:
            self.args['nodeFeatureDim'] = 1
        if self.args['loss'] == "kl":
            self.criterion = nn.KLDivLoss(reduction='batchmean')
        elif self.args['loss'] == "mse":
            self.criterion = RMSE()

        if self.args['baseModel'] == "DeepGraphlet":
            self.model = DeepGraphlet(nfeat=self.args['nodeFeatureDim'], nhid=self.args['hiddenDim'],
                                      nlayer=self.args['numLayer'], nclasses=self.args['nclasses'],
                                      mlpPos=self.args['mlpPos'], useDropout=self.args['useDropout'],
                                      keepProb=self.args['keepProb'], useBatchNorm=self.args['useBatchNorm'])
        elif self.args['baseModel'] == "GIN":
            self.model = GIN(nfeat=self.args['nodeFeatureDim'], nhid=self.args['hiddenDim'],
                             nlayer=self.args['numLayer'], nclasses=self.args['nclasses'], mlpPos=self.args['mlpPos'],
                             useDropout=self.args['useDropout'], keepProb=self.args['keepProb'],
                             useBatchNorm=self.args['useBatchNorm'])
        elif self.args['baseModel'] == "GCN":
            self.model = GCN(nfeat=self.args['nodeFeatureDim'], nhid=self.args['hiddenDim'],
                             nlayer=self.args['numLayer'], nclasses=self.args['nclasses'], mlpPos=self.args['mlpPos'],
                             useDropout=self.args['useDropout'], keepProb=self.args['keepProb'],
                             useBatchNorm=self.args['useBatchNorm'])
        elif self.args['baseModel'] == "KMLP":
            self.model = KMLP(self.args['nodeFeatureDim'], self.args['hiddenDim'], [2, 6, 21],
                              useDropout=self.args['useDropout'], keepProb=self.args['keepProb'],
                              useBatchNorm=self.args['useBatchNorm'])

    def load_result_writter(self, result_writter):
        self.resultWritter = result_writter

    def SaveModel(self, modelPath):
        torch.save(self.model.state_dict(), modelPath)

    def LoadModel(self, modelPath):
        self.model.load_state_dict(torch.load(modelPath, map_location=torch.device('cpu')))

        # self.model.load_state_dict(torch.load(modelPath,,map_location=torch.device('cpu')))

    def GenerateLabel(self, nodeCnt, path):
        fileName = path.split('/')[-1].split('.')[0]
        items = path.split('/')
        prefix = ""
        for i in range(len(items) - 1):
            prefix += items[i] + "/"
        outFile = prefix + fileName + ".out"
        df = pd.read_csv(outFile, sep=' ', header=None).iloc[:, :-1]
        rawLabel = np.array(df)

        orbits = [1, 2, 1, 2, 2, 1, 3, 2, 1, 3, 4, 2, 3, 4, 3, 1, 4, 4, 2, 4, 2, 3, 2, 3, 3, 3, 3, 2, 2, 1]
        motifs = np.zeros((nodeCnt, 30), dtype=np.float64)
        cnt = 0
        st = 0
        for length in orbits:
            motifs[:, cnt] = np.sum(rawLabel[:, st: st + orbits[cnt]], axis=1)
            st += orbits[cnt]
            cnt += 1
        labels = []
        labels.append(motifs[:, 1: 3])
        labels.append(motifs[:, 3: 9])
        labels.append(motifs[:, 9: 30])
        for i in range(len(labels)):
            labels[i] += 1e-10
            labels[i] = labels[i] / np.sum(labels[i], axis=1).reshape((labels[i].shape[0], 1))
        return labels

    def GenerateFeedDict(self, fileName="test", needLabel=True, cpu=False):

        # Do this edge have been cleaned ?
        # ljr: edgeList: [[u1, v1], [u2, v2], ..., ]
        nodeCnt, edgeCnt, edgeList = readEdgeList(fileName)
        nodeFeature = {}
        nodeFeature['raw'] = torch.from_numpy(np.ones((nodeCnt, 1))).float()
        # if self.args['useRandomFeature'] == True:
        # ljr: random feature: dim = 29
        nodeFeature['random'] = torch.from_numpy(np.random.rand(nodeCnt, 29) - 0.5).float()
        # elif self.args['useKTupleFeature'] == True:
        prefix, _ = split_between_last_char(fileName, '.')
        # ljr: what?
        nodeFeature['ktuple'] = torch.from_numpy(np.loadtxt(prefix + ".edges_features5") / 100).float()
        # ???

        indices = np.zeros((2, edgeCnt * 2), dtype=np.int64)
        # deg = []
        # if self.args['baseModel'] == "GCN" or self.args['aggregator'] == 'GCN' or self.args['aggregator'] == "mean":
        deg = [0 for i in range(nodeCnt)]
        for edge in edgeList:
            u, v = edge
            deg[int(u)] += 1
            deg[int(v)] += 1
        for i in range(nodeCnt):
            if deg[i] == 0:
                deg[i] = 1
        #         jishu = 0

        # if self.args['aggregator'] == "sum":
        #     values[edgeCnt] = 1.0
        # elif self.args['aggregator'] == "mean":
        #     values[edgeCnt] = 1.0 / deg[int(u)]
        # if self.args['baseModel'] == "GCN" or self.args['aggregator'] == "GCN":
        #     values[edgeCnt] = 1.0 / deg[int(u)] / deg[int(v)]
        adj = {}
        for aggr in ["sum", "mean", "GCN"]:
            values = np.zeros((edgeCnt * 2), dtype=np.float32)
            cnt = 0
            for edge in edgeList:
                u, v = edge
                indices[0, cnt], indices[1, cnt] = u, v
                if aggr == "sum":
                    values[cnt] = 1.0
                elif aggr == "mean":
                    values[cnt] = 1.0 / deg[int(u)]
                elif aggr == "GCN":
                    values[cnt] = 1.0 / deg[int(u)] / deg[int(v)]
                cnt += 1

                v, u = edge
                indices[0, cnt], indices[1, cnt] = u, v
                if aggr == "sum":
                    values[cnt] = 1.0
                elif aggr == "mean":
                    values[cnt] = 1.0 / deg[int(u)]
                elif aggr == "GCN":
                    values[cnt] = 1.0 / deg[int(u)] / deg[int(v)]
                cnt += 1
            sparseAggregator = torch.sparse.FloatTensor(torch.from_numpy(indices), torch.from_numpy(values),
                                                        torch.Size([nodeCnt, nodeCnt]))
            sparseAggregator = sparseAggregator.float()
            adj[aggr] = sparseAggregator
        labels = []
        if needLabel == True:
            labels = self.GenerateLabel(nodeCnt, fileName)
            for i in range(len(labels)):
                labels[i] = torch.from_numpy(labels[i]).float()

        # nodeFeature = torch.from_numpy(nodeFeature).float()

        edgeIndex = (torch.from_numpy(np.array(edgeList).T.astype(int))).type(torch.LongTensor)
        return nodeFeature, edgeIndex, adj, labels, nodeCnt, edgeCnt

    def loadData(self, filePath, needLabel=True, cpu=False):
        idx = 0
        dataDic = {}
        infoDic = {}
        for path in filePath:
            features, edgeIndex, adj, labels, nodeCnt, edgeCnt = self.GenerateFeedDict(fileName=path,
                                                                                       needLabel=needLabel, cpu=False)
            dataDic[idx] = (features, edgeIndex, adj, labels)
            infoDic[idx] = (nodeCnt, edgeCnt)
            idx += 1
        return dataDic, infoDic

    def train(self, features, adj, labels):
        # print(features[0])
        self.model.train()
        self.optimizer.zero_grad()

        preds = self.model(features, adj)

        losses = []
        loss = 0
        for i in range(len(preds)):
            if self.args['nclasses'][i] == 2:
                idx = 0
            elif self.args['nclasses'][i] == 6:
                idx = 1
            elif self.args['nclasses'][i] == 21:
                idx = 2

            if self.args['loss'] == "kl":
                cur_loss = self.criterion(F.log_softmax(preds[i], dim=1), labels[idx])
                preds[i] = F.softmax(preds[i], dim=1)
            else:
                preds[i] = F.softmax(preds[i], dim=1)
                cur_loss = self.criterion(preds[i], labels[idx])
            # preds[i] = F.softmax(preds[i], dim = 1)
            # if self.args['loss'] == "kl":
            #     cur_loss = self.criterion(torch.log(preds[i]), labels[idx])
            # else:
            #     cur_loss = self.criterion(preds[i], labels[idx])
            loss = loss + cur_loss
            losses.append(cur_loss)
        loss.backward()
        self.optimizer.step()

        return losses, preds, labels

    def eval(self, features, adj, labels, criterion):
        with torch.no_grad():
            self.model.eval()

            preds = self.model(features, adj)
            losses = []
            loss = 0
            for i in range(len(preds)):
                if self.args['nclasses'][i] == 2:
                    idx = 0
                elif self.args['nclasses'][i] == 6:
                    idx = 1
                elif self.args['nclasses'][i] == 21:
                    idx = 2

                if self.args['loss'] == "kl":
                    cur_loss = self.criterion(F.log_softmax(preds[i], dim=1), labels[idx])
                    preds[i] = F.softmax(preds[i], dim=1)
                else:
                    preds[i] = F.softmax(preds[i], dim=1)
                    cur_loss = self.criterion(preds[i], labels[idx])
                loss = loss + cur_loss
                losses.append(cur_loss)

        return losses, preds, labels

    def trainVal(self, synDir):
        precent = 10
        filePath = []
        valPath = []
        for path in synDir:
            filenames = os.listdir(path)
            filenames = [(path + "/" + name) for name in filenames]
            fileNames = []
            for name in filenames:
                if name.split('.')[-1] == "edges":
                    fileNames.append(name)
            np.random.shuffle(fileNames)
            trainNum = int(len(fileNames) / 10 * 7)
            filePath.extend(fileNames[:trainNum])
            valPath.extend(fileNames[trainNum:])
        return filePath, valPath

    def torchList2floatList(self, losses):
        results = []
        for loss in losses:
            results.append(float(loss.to(cpu)))
        return results

    def train_graph(self, modelPath):
        self.model.to(device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.args['learningRate'],
                                    weight_decay=self.args['weightDecay'])

        print(len(self.trainData))
        print(self.args)
        print(modelPath)
        bestValScore = 1e10
        bestValLosses = []
        index = [i for i in range(len(self.trainData))]
        step = len(self.valData) * 2
        time_start = time.time()
        for i in range(self.args['numIterator']):
            if i % len(self.trainData) == 0:
                np.random.shuffle(index)
            idx = index[i % len(self.trainData)]
            features, edgeIndex, adj, labels = self.trainData[idx]
            if self.args['useKTupleFeature'] == True:
                features = features['ktuple']
            elif self.args['useRandomFeature'] == True:
                features = features['random']
            else:
                features = features['raw']
            adj = adj[self.args['aggregator']]
            features, adj = features.to(device), adj.to(device)
            for j in range(len(labels)):
                labels[j] = labels[j].to(device)

            result = self.train(features, adj, labels)
            if (i % step == 0) or (i == self.args['numIterator'] - 1):
                print('------------------------------------------------------------------------')
                print(i)
                print(self.trainInfo[idx])
                print(result[0])
                valScore, valLosses = self.testRealGraph(printInfo=False)
                print(valLosses)
                if valScore < bestValScore:
                    bestValScore = valScore
                    bestValLosses = valLosses
                    self.SaveModel(modelPath)

            # is this trans needed???
            features, adj = features.to(cpu), adj.to(cpu)
            for j in range(len(labels)):
                labels[j] = labels[j].to(cpu)
        print("best valScore: ", bestValScore)
        print("best valLosses: ", bestValLosses)
        self.resultWritter.writeResult('------------------------------------------------------------------------')
        time_end = time.time()
        print("time cost", time_end - time_start, 's')
        self.resultWritter.writeResult("time cost" + str(time_end - time_start) + 's')
        self.resultWritter.writeResult("trainDataNum: " + str(len(self.trainData)))
        self.resultWritter.writeResult("valDataNum: " + str(len(self.valData)))
        self.resultWritter.saveDic(self.args)
        self.resultWritter.writeResult("bestValScore: " + str(float(bestValScore.to(cpu))))
        self.resultWritter.writeResult("bestValLosses: ")
        self.resultWritter.saveListLine(self.torchList2floatList(bestValLosses))
        return bestValScore

    def testRealGraph(self, filePath="", printInfo=True):
        valScore = 0
        lossResult = None
        for i in range(len(self.valData)):
            if printInfo:
                self.resultWritter.saveList(self.valInfo[i])
                print(self.valInfo[i])

            features, _, adj, labels = self.valData[i]

            adj = adj[self.args['aggregator']]
            if self.args['useKTupleFeature']:
                features = features['ktuple']
            elif self.args['useRandomFeature']:
                features = features['random']
            else:
                features = features['raw']
            features, adj = features.to(device), adj.to(device)
            for j in range(len(labels)):
                labels[j] = labels[j].to(device)
            result = self.eval(features, adj, labels, self.criterion)
            # print(result)
            if printInfo:
                self.resultWritter.writeResult(str(result[0]))
                print(result[0])
            if lossResult == None:
                lossResult = list(result[0])
            else:
                for i in range(len(lossResult)):
                    lossResult[i] += result[0][i]
            for item in result[0]:
                valScore += item
        for i in range(len(lossResult)):
            lossResult[i] /= len(self.valData)
        return valScore / len(self.valData), lossResult

    def load_infer_data(self, valData, needLabel=True):
        self.inferData, self.inferInfo = self.loadData(valData, needLabel=needLabel)
        self.inferPath = valData

    def inferRealGraph(self, filePath="", printInfo=True, needLabel=True, write=False):
        print("Enter LoadData")
        self.resultWritter.saveList(self.inferPath)
        self.model.to(cpu)
        for i in range(len(self.inferData)):
            if printInfo:
                self.resultWritter.saveList(self.inferInfo[i])
                print(self.inferInfo[i])
            features, _, adj, labels = self.inferData[i]

            adj = adj[self.args['aggregator']]
            if self.args['useKTupleFeature'] == True:
                features = features['ktuple']
            elif self.args['useRandomFeature'] == True:
                features = features['random']
            else:
                features = features['raw']
            with torch.no_grad():
                if needLabel == True:
                    losses, preds, labels = self.eval(features, adj, labels, self.criterion)
                    print(self.args['loss'] + ": ", losses)
                    self.resultWritter.writeResult(self.args['loss'] + ": ")
                    self.resultWritter.saveListLine(self.torchList2floatList(losses))
                else:
                    self.model.eval()
                    preds = self.model(features, adj)
                # print(features.shape, preds[0].shape, preds[1].shape, preds[2].shape)
                # print(self.criterion(features[:, 0:2], preds[0]))
                # print(self.criterion(features[:, 2:8], preds[1]))
                # print(self.criterion(features[:, 8:], preds[2]))
                # for idx in [100, 1000, 1005, 20000, 30000]:
                #     print('--------------------------------------------')
                #     print(preds[0].shape)
                #     print(preds[0][idx])
                #     print(labels[0][idx])
                #     print(preds[1][idx])
                #     print(labels[1][idx])
                #     print(preds[2][idx])
                #     print(labels[2][idx])
