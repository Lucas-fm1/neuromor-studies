"""===================================================================================
   |  Spiking Neural Network (SNN) with LIF and ALIF Neurons                         |
   | --------------------------------------------------------------------------------|
   | This program implements a simple spiking neural network using Leaky             |
   | Integrate-and-Fire (LIF) and Adaptive Leaky Integrate-and-Fire (ALIF) neurons.  |
   | It compares their behavior and applies the model to a regression task.          |
   | --------------------------------------------------------------------------------|
   | Author: Lucas Farias Martins                                                    |                                            
   | Email:  lucas.martins@ee.ufcg.edu.br                                            |
   | Date:   2025-03-04                                                              |
   ==================================================================================="""

import numpy as np
import matplotlib.pyplot as plt
#===================================================
# LIF class
#===================================================                               
class LIFNeuron:
    """ Standard Leaky Integrate-and-Fire (LIF) neuron model. """
    def __init__(self, tau_m=20.0, V_rest=-65.0, V_th=-50.0, V_reset=-70.0, dt=1.0):
        self.tau_m   = tau_m
        self.V_rest  = V_rest
        self.V_th    = V_th
        self.V_reset = V_reset
        self.dt      = dt
        self.V       = V_rest
        self.spikes  = []

    def step(self, I, t):
        """ Update the neuron state for one time step. """
        dV = (- (self.V - self.V_rest) + I) / self.tau_m
        self.V += dV * self.dt
        
        if self.V >= self.V_th:
            self.spikes.append(t)
            self.V = self.V_reset
#===================================================
# ALIF class
#===================================================                   
class ALIFNeuron(LIFNeuron):
    """ Adaptive Leaky Integrate-and-Fire (ALIF) neuron model with threshold adaptation. """
    def __init__(self, tau_m=20.0, tau_a=200.0, beta=1.5, **kwargs):
        super().__init__(**kwargs)
        self.tau_a = tau_a
        self.beta = beta
        self.a = 0.0
        
    def step(self, I, t):
        dV = (- (self.V - self.V_rest) + I) / self.tau_m
        da = -self.a / self.tau_a
        
        self.V += dV * self.dt
        self.a += da * self.dt
        
        V_th_adaptive = self.V_th + self.a
        
        if self.V >= V_th_adaptive:
            self.spikes.append(t)
            self.V = self.V_reset
            self.a += self.beta
#===================================================
# SNN class
#===================================================
class SNN:
    """
    Spiking Neural Network with multiple neurons.
    """
    def __init__(self, n_neurons, neuron_type, T, I):
        self.n_neurons = n_neurons
        self.T = T
        self.dt = 1.0
        self.neurons = [neuron_type(dt=self.dt) for _ in range(n_neurons)]
        self.I = I

    def run(self):
        """Simulate the network over time."""
        for t in range(self.T):
            for neuron in self.neurons:
                neuron.step(self.I[t], t)

    def plot_spikes(self, title):
        """Plot spike train of the network."""
        plt.figure(figsize=(10, 4))
        for i, neuron in enumerate(self.neurons):
            plt.scatter(neuron.spikes, np.ones_like(neuron.spikes) * i, s=10, label=f"Neuron {i+1}" if i == 0 else "")
        plt.title(title)
        plt.xlabel("Time (ms)")
        plt.ylabel("Neurons")
        plt.legend()
        plt.show()

#=======================================================================================                                                                            
#        //   ) )                                                                  
#       ((        ( )  _   __              //  ___    __  ___ ( )  ___       __    
#         \\     / / // ) )  ) ) //   / / // //   ) )  / /   / / //   ) ) //   ) ) 
#           ) ) / / // / /  / / //   / / // //   / /  / /   / / //   / / //   / /  
#    ((___ / / / / // / /  / / ((___( ( // ((___( (  / /   / / ((___/ / //   / /   
#=======================================================================================

# Simulation parameters
T         = 500          # Total simulation time (ms)
I         = np.zeros(T)
I[50:450] = 5            # Constant input current between 50ms and 450ms
n_neurons = 5            # Number of neurons in the layer

snn_lif = SNN(n_neurons, LIFNeuron, T, I)
snn_lif.run()
snn_lif.plot_spikes("SNN with LIF Neurons")

snn_alif = SNN(n_neurons, ALIFNeuron, T, I)
snn_alif.run()
snn_alif.plot_spikes("SNN with ALIF Neurons")

# Regression task setup
np.random.seed(42)
x = np.linspace(0, 10, T)  # Input values
y = 2 * x + 3 + np.random.normal(0, 2, T)  # Linear function with noise

# Convert input into spike train representation
I_regression = np.interp(x, (x.min(), x.max()), (0, 10))  # Normalize input current

# Train ALIF neurons for regression
snn_regression = SNN(n_neurons, ALIFNeuron, T, I_regression)
snn_regression.run()

# Compute spike count as output
spike_counts = np.array([len(neuron.spikes) for neuron in snn_regression.neurons])
predicted_y  = spike_counts / spike_counts.max() * y.max()

# Plot regression results
plt.figure(figsize=(8, 5))
plt.scatter(x, y, label="True Values", alpha=0.6)
plt.scatter(x[:n_neurons], predicted_y, label="Predicted Values (Spike Count)", color='r')
plt.xlabel("Input")
plt.ylabel("Output")
plt.legend()
plt.title("SNN Regression using ALIF Neurons")
plt.show()