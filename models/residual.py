
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class ResidualLayer(nn.Module):
    """
    One residual layer inputs:
    - in_dim : the input dimension
    - h_dim : the hidden layer dimension
    - res_h_dim : the hidden dimension of the residual block
    """

    def __init__(self, in_dim, h_dim, res_h_dim, type=None):
        super(ResidualLayer, self).__init__()
        if type=='conv':
            self.res_block = nn.Sequential(
                nn.ReLU(True),
                nn.Conv1d(in_dim, res_h_dim, kernel_size=3,
                        stride=1, padding=1, bias=False),
            )
        elif type=='lin':
            self.res_block = nn.Sequential(
                nn.ReLU(True),
                nn.Linear(h_dim, h_dim)
            )


    def forward(self, x):
        x = x + self.res_block(x)
        return x


class ResidualStack(nn.Module):
    """
    A stack of residual layers inputs:
    - in_dim : the input dimension
    - h_dim : the hidden layer dimension
    - res_h_dim : the hidden dimension of the residual block
    - n_res_layers : number of layers to stack
    """

    def __init__(self, in_dim, h_dim, res_h_dim, n_res_layers, type):
        super(ResidualStack, self).__init__()
        self.n_res_layers = n_res_layers
        self.stack = nn.ModuleList(
            [ResidualLayer(in_dim, h_dim, res_h_dim, type)]*n_res_layers)

    def forward(self, x):
        for layer in self.stack:
            x = layer(x)
        x = F.relu(x)
        return x


if __name__ == "__main__":
    # random data
    x = np.random.random_sample((5, 768, 512))
    x = torch.tensor(x).float()
    # test Residual Layer
    print("Input size", x.shape)
    res = ResidualLayer(768, 768, 768)
    res_out = res(x)
    print('Res Layer out shape:', res_out.shape)
    # test res stack
    res_stack = ResidualStack(768, 768, 768, 2)
    res_stack_out = res_stack(x)
    print('Res Stack out shape:', res_stack_out.shape)
