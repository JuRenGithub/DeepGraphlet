import torch
import torch.nn as nn
from MLP import MLP
# from torch_geometric.nn import GINConv
# from torch_geometric.utils import to_undirected
import torch.nn.functional as F
from utils import printCurrentProcessMemory, printItemMemory
import copy
import gc


class KMLP(torch.nn.Module):
    def __init__(self, nfeat, nhid, nclasses, useDropout=False, keepProb=0.5, useBatchNorm=False):
        super(KMLP, self).__init__()
        self.useDropout = useDropout
        self.keepProb = keepProb
        self.useBatchNorm = useBatchNorm
        self.nclasses = nclasses

        self.mlps = nn.ModuleList()
        for i in range(len(nclasses)):
            self.mlps.append(MLP([nfeat, nhid, nclasses[i]], useDropout, keepProb, useBatchNorm))

    def forward(self, features, adj):
        outputs = []

        output = features
        for i in range(len(self.nclasses)):
            tmp = self.mlps[i](output)
            outputs.append(tmp)
        return outputs
