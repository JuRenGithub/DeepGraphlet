import torch
import torch.nn as nn
import torch.nn.functional as F


class MLP(nn.Module):
    def __init__(self, shapes, useDropout = False, keepProb = 0.5, useBatchNorm = False):
        super(MLP, self).__init__()
        length = len(shapes) - 1
        self.linears = nn.ModuleList()
        self.useDropout = useDropout
        self.keepProb = keepProb
        self.useBatchNorm = useBatchNorm
        if self.useBatchNorm == True:
            self.bns = nn.ModuleList()
        
        for i in range(length):
            self.linears.append(nn.Linear(shapes[i], shapes[i + 1]))
            if useBatchNorm == True and i != length - 1:
                self.bns.append(nn.BatchNorm1d(shapes[i + 1]))

    def forward(self, output):
        length = len(self.linears)
        for i in range(length):
            output = self.linears[i](output)
            if i != length - 1:
                if self.useBatchNorm == True:
                    output = self.bns[i](output)
                output = F.relu(output)
                if self.useDropout == True:
                    output = F.dropout(output, p = self.keepProb, training=self.training)
        
        return output