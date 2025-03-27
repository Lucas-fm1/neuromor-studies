import numpy as np
import matplotlib.pyplot as plt

def poisson_spike_train(rate, duration):
    spikes = []
    t = 0
    while t < duration:
        t += -np.log(np.random.rand()) / rate
        if t < duration:
            spikes.append(t)
    return np.array(spikes)

# Parâmetros
rate     = 10   # Hz (spikes por segundo)
duration = 5.0  # segundos

# Gerar spikes
spike_times = poisson_spike_train(rate, duration)

# Plot
plt.eventplot(spike_times, lineoffsets=1, colors='black')
plt.xlabel('Tempo (s)')
plt.ylabel('Neuron')
plt.title('Poisson Spike Train')
plt.show()
