import os
from django.shortcuts import render
from django.http import JsonResponse
from scipy.stats import norm
import numpy as np
import tensorflow as tf
from scipy.stats import entropy
import json
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import Aer

generator = tf.keras.models.load_model(os.path.join('../generator3.h5'))

def calculate_entropy(sequence):
    p0 = np.mean(np.array(sequence) == 0)
    p1 = np.mean(np.array(sequence) == 1)
    
    if p0 == 0:
        term0 = 0
    else:
        term0 = -p0 * np.log2(p0)
    
    if p1 == 0:
        term1 = 0
    else:
        term1 = -p1 * np.log2(p1)
    
    entropy = term0 + term1
    return entropy

def monobit_test(sequence):
    seq = np.array(sequence) * 2 - 1
    s = np.sum(seq)
    n = len(sequence)
    s_obs = np.abs(s) / np.sqrt(n)
    p_value = 2 * (1 - norm.cdf(s_obs))
    return p_value

def count_runs(sequence):
    runs = 1 
    for i in range(1, len(sequence)):
        if sequence[i] != sequence[i - 1]: 
            runs += 1
    return runs

def runs_test(sequence):
    n = len(sequence)
    expected_runs = 2 * n / 3
    actual_runs = count_runs(sequence)
    return abs(actual_runs - expected_runs) <= (1.96 * (2 * n / 9) ** 0.5)

def generate_randomness_tests(sequence):
    n = len(sequence)
    monobit_bool = abs(np.sum(sequence) - n / 2) < np.sqrt(n)
    monobit = monobit_test(sequence)
    runs = runs_test(sequence) 
    return {"monobit": float(monobit), "monobitBool": bool(monobit_bool), "runs": bool(runs)}

def generate_key(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        use_quantum = data.get("quantum_method", False)
        num_qubits = 16*4
        latent_dim = 256

        if(use_quantum):
            generated_sequence_resize = generate_key_quantum(num_qubits)
            entropy_value = calculate_entropy(generated_sequence_resize)
            randomness_tests = generate_randomness_tests(generated_sequence_resize)
        else:
            latent_vectors = tf.random.normal((2, latent_dim))
            generated_sequence = generator.predict(latent_vectors).flatten()
            key = np.round(generated_sequence).astype(int)
            generated_sequence_resize = np.resize(key, num_qubits)
            entropy_value = calculate_entropy(generated_sequence_resize)
            randomness_tests = generate_randomness_tests(generated_sequence_resize)

        return JsonResponse({
            "key": ''.join(map(str, generated_sequence_resize)),
            "entropy": float(entropy_value),
            "randomness_tests": randomness_tests
        })
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


def generate_key_quantum(num_qubits):
    qreg_q = QuantumRegister(num_qubits, 'q')
    creg_c = ClassicalRegister(num_qubits, 'c')
    circuit = QuantumCircuit(qreg_q, creg_c)
    for i in range(0, num_qubits):
        circuit.h(qreg_q[i])
        circuit.measure(qreg_q[i], creg_c[i])

    simulator = Aer.get_backend('qasm_simulator')
    shots = 1
    result = simulator.run(circuit, shots=shots).result()
    counts = result.get_counts()
    quantum_sequence = np.array([int(bit) for seq in counts.keys() for bit in seq])

    return quantum_sequence