"""===================================================================================
   |  Spiking Neural Network (SNN) with LIF and ALIF Neurons                         |
   | --------------------------------------------------------------------------------|
   | This program implements two neuron models:                                      |
   | Integrate-and-Fire (LIF) and Current-Based (CuBa) neurons.                      |
   | It compares their behavior and applies the model to a spike train.              |
   | --------------------------------------------------------------------------------|
   | Author: Lucas Farias Martins                                                    |
   | Email:  lucas.martins@ee.ufcg.edu.br                                            |
   | Date:   2025-03-24                                                              |
   ==================================================================================="""

import numpy as np
import matplotlib.pyplot as plt

#---------------------------------------------------------
#                       __   ________ 
#                      / /  /  _/ __/ 
#                     / /___/ // _/   
#                    /____/___/_/                                     
#---------------------------------------------------------
def lif_neuron(I, Tau_m, V_rest, V_th, V_reset):
    V = np.full_like(time, V_rest, dtype=float)
    spikes = []

    for t in range(1, len(time)):
        dV = (-(V[t-1] - V_rest) + Rm * I[t]) * (dt / Tau_m)
        V[t] = V[t-1] + dV

        if V[t] >= V_th:
            V[t] = V_reset
            spikes.append(time[t])

    return V, spikes
#---------------------------------------------------------
#                   _____     ___      
#                  / ___/_ __/ _ )___ _
#                 / /__/ // / _  / _ `/
#                 \___/\_,_/____/\_,_/ 
#---------------------------------------------------------
def cuba_neuron(I, Tau_m, Tau_s, V_rest, V_th, V_reset):
    V = np.full_like(time, V_rest, dtype=float)
    g_syn = np.zeros_like(time)  # Condutância sináptica
    spikes = []

    for t in range(1, len(time)):
        # Atualiza a condutância sináptica
        dg = (-g_syn[t-1] + spike_train[t]) * (dt / Tau_s)
        g_syn[t] = g_syn[t-1] + dg

        # Atualiza o potencial de membrana
        I_syn = g_syn[t]
        dV = (-(V[t-1] - V_rest) + Rm * I_syn) * (dt / Tau_m)
        V[t] = V[t-1] + dV

        if V[t] >= V_th:
            V[t] = V_reset
            spikes.append(time[t])

    return V, spikes
# _____________________________________________                                                                            
#    ___ _           _      _   _              |
#   / __(_)_ __ _  _| |__ _| |_(_)___ _ _      |
#   \__ \ | '  \ || | / _` |  _| / _ \ ' \     |
#   |___/_|_|_|_\_,_|_\__,_|\__|_\___/_||_|    |
# _____________________________________________|
# ___________________________ Parâmetros comuns
T    = 200  # Tempo total de simulação (ms)
dt   = 0.1  # Passo de tempo (ms)
time = np.arange(0, T, dt)
# _____________________________________________
# ______________________ Parâmetros do neurônio
V_rest  = -65  # Potencial de repouso (mV)
V_th    = -50  # Limiar de disparo (mV)
V_reset = -65  # Potencial de reset (mV)
I_ext   = 1.5  # Corrente de entrada (nA)
# _____________________________________________
# ______________________ Parâmetros específicos
Rm    = 10       # Resistência da membrana (MΩ)
Cm    = 1        # Capacitância da membrana (nF)
Tau_m = Rm * Cm  # Constante de tempo da membrana (ms)
Tau_s = 5        # Constante de tempo sináptica (Para o modelo CuBa)
# _____________________________________________
# ______________________________ Trem de spikes
spike_train = np.zeros_like(time)
spike_times = np.arange(20, 200, 40)  # Spikes a cada 40 ms
spike_train[np.searchsorted(time, spike_times)] = 1

# Corrente de entrada (constante para LIF, induzida por spikes para CuBa)
I_lif  =  np.ones_like(time) * I_ext
I_cuba =  np.zeros_like(time)
I_cuba += spike_train

V_lif, spikes_lif = lif_neuron(I_lif, Tau_m, V_rest, V_th, V_reset)
V_cuba, spikes_cuba = cuba_neuron(I_cuba, Tau_m, Tau_s, V_rest, V_th, V_reset)

# Plotando os resultados
plt.figure(figsize=(12, 8))

plt.subplot(3, 1, 1)
plt.plot(time, spike_train, label='Spike Train', color='black')
plt.ylabel('Entrada (spikes)')
plt.legend()

plt.subplot(3, 1, 2)
plt.plot(time, V_lif, label='LIF Neuron')
plt.axhline(y=V_th, color='r', linestyle='--', label='Threshold')
plt.ylabel('V (mV)')
plt.legend()

plt.subplot(3, 1, 3)
plt.plot(time, V_cuba, label='CuBa Neuron', color='orange')
plt.axhline(y=V_th, color='r', linestyle='--')
plt.ylabel('V (mV)')
plt.xlabel('Tempo (ms)')
plt.legend()

plt.tight_layout()
plt.show()
