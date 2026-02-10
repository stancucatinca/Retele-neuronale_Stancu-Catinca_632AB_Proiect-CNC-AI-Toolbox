import torch.nn as nn

class CNCModel(nn.Module):
    
    def __init__(self, input_size=5, hidden_size=128, output_size=1):
        super(CNCModel, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, hidden_size),  # Stratul 1: 5 -> 128
            nn.ReLU(),
            nn.Linear(hidden_size, 16),          # Stratul 2: 128 -> 16 (am crescut si aici putin de la 8 la 16 ca sa aiba sens)
            nn.ReLU(),
            nn.Linear(16, output_size)           # Stratul 3: 16 -> 1
        )

    def forward(self, x):
        return self.layers(x)