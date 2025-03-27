"""===================================================================================
   | Cross-entropy loss for SNNs training on classification problem                  |
   | Techniques: rate-coded cross-entropy and surrogate gradient                     |
   |---------------------------------------------------------------------------------|
   | Author: Lucas Farias Martins                                                    |                                            
   | Email:  lucas.martins@ee.ufcg.edu.br                                            |
   | Date:   2025-03-25                                                              |
   ==================================================================================="""
   
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
# _______________________________________________________________________
# __________________________ Rate-coded spike output (soft approximation)
def spike_rate(spike_train):
    return spike_train.sum(dim=1) / spike_train.size(1)  # Sum over time axis
# _______________________________________________________________________
# _________________________ Surrogate gradient with sigmoid approximation
class SpikeActivation(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x):
        ctx.save_for_backward(x)  # Save input for backward pass
        return (x > 0).float()    # Binary spike (0 or 1)

    @staticmethod
    def backward(ctx, grad_output):
        x, = ctx.saved_tensors  # Retrieve the saved input
        # Surrogate gradient (sigmoid derivative approximation)
        return grad_output * (1 / (1 + torch.exp(-x)))
# _______________________________________________________________________
# __________________________________________________ Spiking Neuron Layer
class SpikingNeuron(nn.Module):
    def __init__(self, input_size, output_size):
        super(SpikingNeuron, self).__init__()
        self.fc = nn.Linear(input_size, output_size)

    def forward(self, x):
        membrane_potential = self.fc(x)
        spikes = SpikeActivation.apply(membrane_potential)
        return spikes
# _______________________________________________________________________
# ____________________________________ Spiking neural network (SNN) Model    
class SpikingModel(nn.Module):
    def __init__(self, input_size, output_size):
        super(SpikingModel, self).__init__()
        self.layer = SpikingNeuron(input_size, output_size)

    def forward(self, x, time_steps=20):
        spike_sum = torch.zeros(x.size(0), self.layer.fc.out_features).to(x.device)
        for _ in range(time_steps):
            spikes = self.layer(x)
            spike_sum += spikes  # Accumulate spikes over time
        return spike_sum / time_steps  # Rate-coded output
#  _____________________________________________________________________
# |                _____            __     __  _                        |
# |               / __(_)_ _  __ __/ /__ _/ /_(_)__  ___                |
# |              _\ \/ /  ' \/ // / / _ `/ __/ / _ \/ _ \               |
# |             /___/_/_/_/_/\_,_/_/\_,_/\__/_/\___/_//_/               |
# |_____________________________________________________________________|

# Model Parameters
input_size    = 28 * 28 # 784
output_size   = 10
batch_size    = 64
time_steps    = 20
epochs        = 10
learning_rate = 0.001

# Dataset (MNIST)
transform     = transforms.Compose([transforms.ToTensor()])
train_dataset = datasets.MNIST(root='./data', train=True, transform=transform, download=True)
train_loader  = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

# Initialize Model and Optimizer
device    = 'cuda' if torch.cuda.is_available() else 'cpu'
model     = SpikingModel(input_size, output_size).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

# Training Loop
for epoch in range(epochs):
    total_loss = 0
    correct = 0
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        images = images.view(images.size(0), -1)  # Flatten to [batch_size, 784]

        # Forward pass
        output_rates = model(images, time_steps)

        # Loss calculation
        loss = criterion(output_rates, labels)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        correct += (output_rates.argmax(1) == labels).sum().item()

    print(f"Epoch [{epoch+1}/{epochs}], Loss: {total_loss:.4f}, Accuracy: {correct / len(train_dataset) * 100:.2f}%")
