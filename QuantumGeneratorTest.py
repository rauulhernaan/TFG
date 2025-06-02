from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import Aer
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import depolarizing_error
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np
import random
import os
import tensorflow as tf
import numpy as np
import scipy.stats as stats
from math import log2

q_bits = 16
qreg_q = QuantumRegister(q_bits, 'q')
creg_c = ClassicalRegister(q_bits, 'c')
circuit = QuantumCircuit(qreg_q, creg_c)
for i in range(0, q_bits):
    circuit.h(qreg_q[i])
    circuit.measure(qreg_q[i], creg_c[i])

# circuit.draw(output='mpl')
# plt.show()

simulator = Aer.get_backend('qasm_simulator')
shots = 10000
result = simulator.run(circuit, shots=shots).result()
counts = result.get_counts()
quantum_sequences = np.array([list(map(int, list(seq))) for seq in counts.keys()])

percentages = {key: (value / shots) * 100 for key, value in counts.items()}

bit_counts = np.zeros((q_bits, 2))

for bitstring, freq in counts.items():
    for i, bit in enumerate(reversed(bitstring)):
        bit_counts[i, int(bit)] += freq


bit_probs = bit_counts / shots

x = np.arange(q_bits)
plt.figure(figsize=(10,5))
plt.bar(x - 0.2, bit_probs[:, 0], width=0.4, label='P(0)', color='red')
plt.bar(x + 0.2, bit_probs[:, 1], width=0.4, label='P(1)', color='green')
plt.xticks(x, [f'Q{i}' for i in range(q_bits)])
plt.xlabel('Qubits')
plt.ylabel('Probabilidad')
plt.title('Probabilidad de obtener 0 y 1 en cada qubit')
plt.legend()
plt.show()

generator = tf.keras.models.load_model('generator3.h5', compile=False)


num_sequences = 10000
latent_dim = 256

latent_vectors = tf.random.normal((num_sequences, latent_dim))
generated_sequence = generator.predict(latent_vectors).flatten()
key = np.round(generated_sequence).astype(int)
generated_sequences = np.resize(key, (num_sequences, q_bits))


prob_zeros = np.mean(generated_sequences == 0, axis=0)
prob_ones = np.mean(generated_sequences == 1, axis=0)

x = np.arange(q_bits)
plt.figure(figsize=(10, 5))
plt.bar(x - 0.2, prob_zeros, width=0.4, label='P(0)', color='red')
plt.bar(x + 0.2, prob_ones, width=0.4, label='P(1)', color='green')
plt.xticks(x, [f'Q{i}' for i in range(q_bits)])
plt.xlabel('Bits')
plt.ylabel('Probabilidad')
plt.title('Probabilidad de obtener 0 y 1 en cada bit (IA Generativa)')
plt.legend()
plt.show()

def runs_test(sequence):
    runs = 1 + np.sum(sequence[:-1] != sequence[1:])
    expected_runs = (2 * len(sequence) - 1) / 3
    std_dev = np.sqrt((16 * len(sequence) - 29) / 90)
    z_score = abs(runs - expected_runs) / std_dev
    p_value = 2 * (1 - stats.norm.cdf(z_score))
    return p_value

def block_frequency_test(sequence, block_size=8):
    """Divide la secuencia en bloques y mide la proporción de 1s en cada uno."""
    num_blocks = len(sequence) // block_size
    proportions = np.array([np.mean(sequence[i * block_size:(i + 1) * block_size]) for i in range(num_blocks)])
    chi_square = 4 * block_size * np.sum((proportions - 0.5) ** 2)
    p_value = 1 - stats.chi2.cdf(chi_square, df=num_blocks - 1)
    return p_value

def longest_run_test(sequence, block_size=8):
    """Mide si hay secuencias de solo 0s o solo 1s más largas de lo esperado."""
    max_run = max(map(len, ''.join(map(str, sequence)).split('0')))
    expected_max = log2(len(sequence))
    return abs(max_run - expected_max) / expected_max

def shannon_entropy(sequence):
    """Calcula la entropía de Shannon de la secuencia."""
    prob_0 = np.mean(sequence == 0)
    prob_1 = np.mean(sequence == 1)
    entropy = -sum(p * log2(p) for p in [prob_0, prob_1] if p > 0)
    return entropy

def calculate_entropy(sequence):
    """Calcula la entropía binaria de una secuencia."""
    # Calcular las probabilidades de 0 y 1
    p0 = np.mean(np.array(sequence) == 0)
    p1 = np.mean(np.array(sequence) == 1)
    
    # Manejo de casos donde p0 o p1 es 0 (para evitar log2(0))
    if p0 == 0:
        term0 = 0
    else:
        term0 = -p0 * np.log2(p0)
    
    if p1 == 0:
        term1 = 0
    else:
        term1 = -p1 * np.log2(p1)
    
    # Entropía binaria
    entropy = term0 + term1
    return entropy

def monobit_test(sequence):
    count_ones = np.sum(sequence)
    count_zeros = len(sequence) - count_ones
    s_n = abs(count_ones - count_zeros) / np.sqrt(len(sequence))
    p_value = 2 * (1 - stats.norm.cdf(s_n))
    return p_value

results_ia = {
    'runs': np.mean([runs_test(seq) for seq in generated_sequences]),
    'block_freq': np.mean([block_frequency_test(seq) for seq in generated_sequences]),
    'longest_run': np.mean([longest_run_test(seq) for seq in generated_sequences]),
    'entropy': np.mean([shannon_entropy(seq) for seq in generated_sequences]),
    'binary_entropy': np.mean([calculate_entropy(seq) for seq in generated_sequences]),
    'monobit': np.mean([monobit_test(seq) for seq in generated_sequences])
}

results_q = {
    'runs': np.mean([runs_test(seq) for seq in quantum_sequences]),
    'block_freq': np.mean([block_frequency_test(seq) for seq in quantum_sequences]),
    'longest_run': np.mean([longest_run_test(seq) for seq in quantum_sequences]),
    'entropy': np.mean([shannon_entropy(seq) for seq in quantum_sequences]),
    'binary_entropy': np.mean([calculate_entropy(seq) for seq in quantum_sequences]),
    'monobit': np.mean([monobit_test(seq) for seq in quantum_sequences])
}

secuencias = []
for _ in range(shots):
    # Genera un número entero aleatorio de longitud bits y lo convierte en lista de bits
    bits = bin(random.getrandbits(q_bits))[2:].zfill(q_bits)
    secuencia = [int(bit) for bit in bits]
    secuencias.append(secuencia)
sec = np.array(secuencias)

print(sec[0], sec[1])

prob_zeros_normal = np.mean(sec == 0, axis=0)
prob_ones_normal = np.mean(sec == 1, axis=0)

x = np.arange(q_bits)
plt.figure(figsize=(10, 5))
plt.bar(x - 0.2, prob_zeros_normal, width=0.4, label='P(0)', color='red')
plt.bar(x + 0.2, prob_ones_normal, width=0.4, label='P(1)', color='green')
plt.xticks(x, [f'Q{i}' for i in range(q_bits)])
plt.xlabel('Bits')
plt.ylabel('Probabilidad')
plt.title('Probabilidad de obtener 0 y 1 en cada bit (Tradicional)')
plt.legend()
plt.show()


results_tradicional = {
    'runs': np.mean([runs_test(seq) for seq in sec]),
    'block_freq': np.mean([block_frequency_test(seq) for seq in sec]),
    'longest_run': np.mean([longest_run_test(seq) for seq in sec]),
    'entropy': np.mean([shannon_entropy(seq) for seq in sec]),
    'binary_entropy': np.mean([calculate_entropy(seq) for seq in sec]),
    'monobit': np.mean([monobit_test(seq) for seq in sec])
}

labels = list(results_ia.keys())
values_ia = list(results_ia.values())
values_q = list(results_q.values())
values_trad = list(results_tradicional.values())

x = np.arange(len(labels))
width = 0.30

fig, ax = plt.subplots()
rects1 = ax.bar(x - width, values_ia, width, label='IA')
rects2 = ax.bar(x , values_q, width, label='Quantum')
rects3 = ax.bar(x + width, values_trad, width, label='Trad')

ax.set_ylabel('Valores')
ax.set_title('Comparación de pruebas de aleatoriedad')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

plt.show()
