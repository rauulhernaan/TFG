import os
from django.shortcuts import render
from django.http import JsonResponse
from scipy.stats import norm
import numpy as np
import tensorflow as tf
from scipy.stats import entropy
from tensorflow.keras.models import load_model
import json

# Cargar el modelo de IA
generator = load_model(os.path.join('../generator.h5'))

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
    # Convertimos la secuencia a +1 y -1
    seq = np.array(sequence) * 2 - 1
    # Calculamos la suma y normalizamos
    s = np.sum(seq)
    n = len(sequence)
    s_obs = np.abs(s) / np.sqrt(n)
    p_value = 2 * (1 - norm.cdf(s_obs))  # Valor p usando la normal estándar
    return p_value

def count_runs(sequence):
    runs = 1  # Inicia con el primer bit como un "run"
    for i in range(1, len(sequence)):
        if sequence[i] != sequence[i - 1]:  # Si el bit cambia, es un nuevo "run"
            runs += 1
    return runs

def runs_test(sequence):
    n = len(sequence)
    expected_runs = 2 * n / 3
    actual_runs = count_runs(sequence)
    # Verificar si el número de runs está dentro de un rango razonable
    return abs(actual_runs - expected_runs) <= (1.96 * (2 * n / 9) ** 0.5)

def generate_randomness_tests(sequence):
    """Ejecuta pruebas básicas de aleatoriedad."""
    n = len(sequence)
    monobit_bool = abs(np.sum(sequence) - n / 2) < np.sqrt(n)
    monobit = monobit_test(sequence)
    runs = runs_test(sequence)  # Ejemplo: verificar si hay secuencias largas de 0 o 1
    return {"monobit": float(monobit), "monobitBool": bool(monobit_bool), "runs": bool(runs)}

def generate_key(request):
    if request.method == 'POST':

        """Genera una clave, calcula su entropía y realiza pruebas de aleatoriedad."""
        latent_dim = 256
        data = json.loads(request.body)
        num_qubits = data.get("message_length", "")*4+4
        latent_vectors = tf.random.normal((num_qubits, latent_dim))
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
