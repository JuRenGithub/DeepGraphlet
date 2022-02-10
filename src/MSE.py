import torch
import torch.nn as nn
import numpy as np
class RMSE(nn.Module):
    def __init__(self):
        super().__init__()
        self.mse = torch.nn.MSELoss()
        
    def forward(self, yhat, y):
        return self.mse(yhat, y)
        # return torch.sqrt(self.mse(yhat, y))
    
if __name__ == '__main__':
    loss = RMSE()
    yhat = torch.tensor([[1., 2.],
                     [2., 3.]])
    y = torch.tensor([[3., 5.],
                  [6., 8.]])
    print(loss(yhat, y))