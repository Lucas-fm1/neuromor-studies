import snntorch as snn
import torch
from snntorch import spikegen
"""
def lif(X, U):
    beta  = 0.9    # set decay rate
    W     = 0.5    # learnable parameter
    theta = 1      # set threshold
    S     = 0      # initialize output spike
    U     = beta * U + W*X - S * theta 
    S     = int(S > theta) # Eq. 5
    return S, U

lif = snn.Leaky(beta=0.9, threshold=1) # initialize neuron

# all thresholds default to threshold=1
lif      = snn.Leaky(beta=0.9)                        # vanilla leaky integrate-and-fire neuron
int_fire = snn.Leaky(beta=1.0)                        # integrate-and-fire neuron
cuba     = snn.Synaptic(beta=0.9, alpha=0.8)          # current-based neuron
rlif_1   = snn.RLeaky(beta=0.9, all_to_all=True)      # all-to-all recurrent lif neuron
rlif_2   = snn.RLeaky(beta=0.9, all_to_all=False)     # one-to-one recurrent lif neuron
slstm    = snn.SLSTM(input_size=10, hidden_size=1000) # spiking LSTM: 10 inputs, 1000 outputs

X = torch.rand(10)  # vector of 10 random inputs
U = torch.zeros(10) # initialize hidden states of 10 neurons to 0 V

infinite_loop = True
while infinite_loop:
    S, U = lif(X*W, U) # Eq.4 and Eq. 5 are recurrently returned
    
"""
steps = 100 # number of time steps

X = torch.rand(10) # vector of 10 random inputs
S = spikegen.rate(X, num_steps=steps)

print(X.size())
print(S.size())