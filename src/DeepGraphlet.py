import torch
import torch.nn as nn
from MLP import MLP
import torch.nn.functional as F
from utils import printCurrentProcessMemory, printItemMemory
import copy
import gc

        
class DeepGraphlet(torch.nn.Module):
    def __init__(self, nfeat, nhid, nlayer, nclasses, mlpPos, loss = "kl", useDropout = False, keepProb = 0.5, useBatchNorm = False):
        super(DeepGraphlet, self).__init__()
        self.nlayer = nlayer
        self.mlpPos = mlpPos
        self.useDropout = useDropout
        self.keepProb = keepProb
        self.useBatchNorm = useBatchNorm
        self.loss = loss
        
        self.MLPs = nn.ModuleList()
        self.bns = nn.ModuleList()
        self.rnns = nn.ModuleList()
        for i in range(nlayer):
            self.MLPs.append(MLP([nhid, nhid, nhid], useDropout, keepProb, useBatchNorm))
            if self.useBatchNorm == True:
                self.bns.append(nn.BatchNorm1d(nhid))
            self.rnns.append(torch.nn.GRUCell(nhid, nhid, bias=True))
                
        
        self.mlp1 = MLP([nfeat, nhid], useDropout, keepProb, useBatchNorm)
        if self.useBatchNorm == True:
            self.bn1 = nn.BatchNorm1d(nhid)
        self.outputers = nn.ModuleList()
        for i in range(len(mlpPos)):
            self.outputers.append(MLP([nhid, nhid, nclasses[i]], useDropout, keepProb, useBatchNorm))

        
    def forward(self, features, adj):
        outputs = []
        
        output = self.mlp1(features)
        if self.useBatchNorm:
            output = self.bn1(output)
        output = F.relu(output)
        # if self.useDropout:
        #     output = F.dropout(output, p = self.keepProb, training=self.training)
        layerInfo = output.clone()
        for i in range(self.nlayer):
            gc.collect()
            output = torch.spmm(adj, output)
            output = self.rnns[i](output, layerInfo)
            output = self.MLPs[i](output)
            
            if self.useBatchNorm:
                output = self.bns[i](output)
            output = F.relu(output)
            if self.useDropout:
                output = F.dropout(output, p = self.keepProb, training=self.training)
            for j in range(len(self.mlpPos)):
                if (i == self.mlpPos[j]):
                    tmp = self.outputers[j](output)
                    outputs.append(tmp)
            layerInfo = output.clone()
        return outputs