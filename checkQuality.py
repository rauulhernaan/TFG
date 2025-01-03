from scipy.stats import entropy
import numpy as np
import tensorflow as tf
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LeakyReLU, BatchNormalization, Dropout

# Generar Secuencias Aleatorias Complejas
def generate_sequences(num_samples, seq_length):
    # 1. Secuencias completamente aleatorias
    pure_random = np.random.randint(0, 2, (num_samples // 3, seq_length))

    # 2. Secuencias con patrones predefinidos (alternancia con ruido)
    patterned_sequences = np.zeros((num_samples // 3, seq_length))
    for i in range(num_samples // 3):
        patterned_sequences[i] = [j % 2 for j in range(seq_length)]  # Alternancia
    patterned_sequences += np.random.normal(0, 0.1, patterned_sequences.shape)  # Ruido
    patterned_sequences = np.clip(patterned_sequences, 0, 1).astype(int)

    # 3. Secuencias sesgadas (70% de 1s)
    biased_sequences = np.random.choice([0, 1], size=(num_samples // 3, seq_length), p=[0.3, 0.7])

    # Combinar y barajar
    dataset = np.vstack((pure_random, patterned_sequences, biased_sequences))
    np.random.shuffle(dataset)
    return dataset

# Parámetros del dataset
num_samples = 5000
seq_length = 32

# Generar dataset
dataset = generate_sequences(num_samples, seq_length)

latent_dim = 256
seq_length = 32

def build_generator(latent_dim, seq_length):
    model = Sequential()
    model.add(Dense(128, input_dim=latent_dim))  # Más unidades iniciales
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.2))
    
    model.add(Dense(256))  # Incrementar gradualmente
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.2))
    model.add(Dropout(0.3))
    
    model.add(Dense(128))  # Reducir hacia la salida
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.2))
    
    model.add(Dense(seq_length, activation="sigmoid"))  # Salida final
    return model

# Crear modelos
generator = build_generator(latent_dim, seq_length)

generator.load_weights(os.path.join('archive', 'generator.h5'))

seqs = generator.predict(tf.random.normal((16, latent_dim)))

# Visualizar secuencias generadas
# Binarizar secuencias: Umbral en 0.5
binary_sequences = (seqs > 0.5).astype(int)



def calculate_entropy(sequence):
    """Calcula la entropía de una secuencia binaria."""
    # Calcular la frecuencia de 0s y 1s
    value_counts = [sequence.count(0), sequence.count(1)]
    probabilities = [count / len(sequence) for count in value_counts]
    return entropy(probabilities, base=2)

# Calcular entropía para cada secuencia generada
entropies = [calculate_entropy(seq.tolist()) for seq in binary_sequences]

# Mostrar resultados
for i, ent in enumerate(entropies, 1):
    print(f"Secuencia {i} - Entropía: {ent:.4f}")