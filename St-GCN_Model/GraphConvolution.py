import torch
import torch.nn as nn
import torch.nn.functional as F

class GraphConv(nn.Module):
    def __init__(self, in_channels, out_channels, adjacency_matrix):
        super(GraphConv, self).__init__()
        self.A = adjacency_matrix
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=(1, 1))

    def forward(self, x):
        # Change einsum to correctly apply adjacency matrix on nodes dimension
        x = torch.einsum('vw,bctw->bctw', self.A, x)  # Apply graph convolution on nodes
        x = self.conv(x)
        return x

class STGCN(nn.Module):
    def __init__(self, in_channels=3, num_nodes=33, num_classes=10, num_frames=60):
        super(STGCN, self).__init__()

        self.A = torch.eye(num_nodes)  # Placeholder adjacency matrix
        
        self.graph_conv1 = GraphConv(in_channels, 64, self.A)
        self.graph_conv2 = GraphConv(64, 128, self.A)
        self.graph_conv3 = GraphConv(128, 256, self.A)
        
        self.temporal_conv1 = nn.Conv2d(64, 64, kernel_size=(3, 1), padding=(1, 0))
        self.temporal_conv2 = nn.Conv2d(128, 128, kernel_size=(3, 1), padding=(1, 0))
        self.temporal_conv3 = nn.Conv2d(256, 256, kernel_size=(3, 1), padding=(1, 0))
        
        self.fc = nn.Linear(256 * num_nodes, num_classes)

    def forward(self, x):
        x = self.graph_conv1(x)  
        x = F.relu(self.temporal_conv1(x))  

        x = self.graph_conv2(x)
        x = F.relu(self.temporal_conv2(x))

        x = self.graph_conv3(x)
        x = F.relu(self.temporal_conv3(x))

        x = x.mean(dim=2)  # Global pooling over time
        x = x.view(x.size(0), -1)
        x = self.fc(x)

        return x
