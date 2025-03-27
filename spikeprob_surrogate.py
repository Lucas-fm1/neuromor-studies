"""
=====================================================================================
| Spiking Neural Network (SNN) with Spike Probability and Surrogate Gradients       |
|-----------------------------------------------------------------------------------|
| Purpose: Demonstrates an SNN model using spike probability                        |
|          with surrogate gradients for training on classification tasks.           |
| Author: Lucas Farias Martins                                                      |
| Email: lucas.martins@ee.ufcg.edu.br                                               |
| Date: 2025-03-26                                                                  |
=====================================================================================
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from tqdm import tqdm

# ----------------------------------------------
# Custom Spike Activation (Surrogate Gradient)
# ----------------------------------------------
class SpikeFunction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, input):
        # Binary spike output (0 or 1)
        spike_output = (input > 0).float()
        ctx.save_for_backward(input)
        return spike_output

    @staticmethod
    def backward(ctx, grad_output):
        input, = ctx.saved_tensors
        # Surrogate gradient approximation (sigmoid derivative)
        grad_input = grad_output * (1 / (1 + torch.exp(-10 * input)))
        return grad_input

# ----------------------------------------------
#            Spiking Neuron Layer
# ----------------------------------------------
class SpikingNeuron(nn.Module):
    def __init__(self, input_size, output_size):
        super(SpikingNeuron, self).__init__()
        self.fc = nn.Linear(input_size, output_size)
        self.threshold = 1.0

    def forward(self, x):
        # Apply spike function with surrogate gradient
        membrane_potential = self.fc(x)
        spikes = SpikeFunction.apply(membrane_potential - self.threshold)
        return spikes, membrane_potential

# ----------------------------------------------
#           SNN Model (2-layer SNN)
# ----------------------------------------------
class SNNModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(SNNModel, self).__init__()
        self.hidden = SpikingNeuron(input_size, hidden_size)
        self.output = SpikingNeuron(hidden_size, output_size)

    def forward(self, x, time_steps=20):
        batch_size = x.size(0)
        
        # Spike accumulation over time
        output_spike_sum = torch.zeros(batch_size, self.output.fc.out_features).to(x.device)
        
        for t in range(time_steps):
            hidden_spikes, _ = self.hidden(x)
            output_spikes, _ = self.output(hidden_spikes)
            
            # Accumulate spikes over time
            output_spike_sum += output_spikes

        # Return spike rates (spike probability approximation)
        spike_rate = output_spike_sum / time_steps
        return spike_rate

# ----------------------------------------------
#           Training the SNN Model
# ----------------------------------------------
def train(model, dataloader, criterion, optimizer, epochs=10, time_steps=20, device='cpu'):
    model.to(device)
    model.train()

    for epoch in range(epochs):
        total_loss = 0
        correct    = 0
        total      = 0

        progress_bar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs}")
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            images = images.view(images.size(0), -1)  # Flatten input
            
            outputs = model(images, time_steps=time_steps) # Forward pass through time
            loss    = criterion(outputs, labels)           # Compute loss
            
            optimizer.zero_grad() # Backpropagation
            loss.backward()       #  
            optimizer.step()      #  

            total_loss  += loss.item()
            _, predicted = outputs.max(1)
            correct     += predicted.eq(labels).sum().item()
            total       += labels.size(0)

            accuracy = 100 * correct / total
            progress_bar.set_postfix(loss=total_loss / (total / batch_size), accuracy=accuracy)

# -----------------------------------------------------------------
#                      __  __   _   ___ _  _ 
#                     |  \/  | /_\ |_ _| \| |
#                     | |\/| |/ _ \ | || .` |
#                     |_|  |_/_/ \_\___|_|\_|
# -----------------------------------------------------------------
if __name__ == '__main__':
    input_size  = 28 * 28  ;  learning_rate = 0.001
    hidden_size = 256      ;  epochs        = 10
    output_size = 10       ;  time_steps    = 20
    batch_size  = 64

    # Load dataset (MNIST Example)
    from torchvision import datasets, transforms
    from torch.utils.data import DataLoader

    transform     = transforms.Compose([transforms.ToTensor()])
    train_dataset = datasets.MNIST(root='./data', train=True, transform=transform, download=True)
    train_loader  = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    # Initialize model, loss function, and optimizer
    model     = SNNModel(input_size, hidden_size, output_size)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # Train model
    train(model, train_loader, criterion, optimizer, epochs, time_steps)

