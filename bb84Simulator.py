import os
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import Aer
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import depolarizing_error
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LeakyReLU, BatchNormalization, Dropout

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

generator.load_weights(os.path.join('generator.h5'))

# --- Paso 1: Generación de claves con el modelo de IA ---
# Suponemos que ya tienes un modelo entrenado llamado `generator`
def generate_ia_key(generator, num_qubits, latent_dim=256):
    latent_vectors = tf.random.normal((num_qubits, latent_dim))  # Generar ruido latente
    generated_sequences = generator.predict(latent_vectors)  # Generar secuencias
    sequence = np.round(generated_sequences).astype(int).flatten()  # Redondear a 0/1
    
    # Repetir o cortar para ajustarse a num_qubits
    return np.resize(sequence, num_qubits)



# Configuración
num_qubits = 200
alice_bits = generate_ia_key(generator, num_qubits, latent_dim)  # Bits generados por IA
alice_bases = np.random.choice(['z', 'x'], num_qubits)  # Bases de Alice

# --- Paso 2: Construcción de circuitos en Qiskit ---
def encode_qubits(bits, bases):
    circuits = []
    for bit, base in zip(bits, bases):
        qr = QuantumRegister(1, name="q")
        cr = ClassicalRegister(1, name="c")
        qc = QuantumCircuit(qr, cr)
        
        if bit == 1:
            qc.x(qr[0])  # Aplicar X si el bit es 1
        if base == 'x':
            qc.h(qr[0])  # Aplicar H para cambiar a la base diagonal
            
        circuits.append(qc)
    return circuits

alice_qubits = encode_qubits(alice_bits, alice_bases)

# --- Paso 3: Crear un modelo de ruido ---
noise_model = NoiseModel()
depolarizing_prob = 0.05  # Probabilidad de error en el canal
error = depolarizing_error(depolarizing_prob, 1)  # Canal depolarizante de 1 qubit
noise_model.add_all_qubit_quantum_error(error, ['id', 'u3', 'u2', 'u1', 'measure'])

# --- Paso 3: Intercepción de Eve ---
eve_bases = np.random.choice(['z', 'x'], num_qubits)  # Eve elige bases al azar
intercepted_results = []

simulator = Aer.get_backend('qasm_simulator')

for i, base in enumerate(eve_bases):
    qc = alice_qubits[i].copy()  # Obtener el circuito de Alice
    if base == 'x':
        qc.h(0)  # Cambiar a base diagonal si Eve usa 'x'
    qc.measure(0, 0)  # Medición de Eve
    job = simulator.run(qc, noise_model=noise_model, shots=1)
    result = job.result()
    counts = result.get_counts(qc)
    intercepted_results.append(int(max(counts, key=counts.get)))

# Eve reenvía los qubits según sus mediciones
eve_encoded_qubits = encode_qubits(intercepted_results, eve_bases)

# --- Paso 4: Bob mide los qubits ---
bob_bases = np.random.choice(['z', 'x'], num_qubits)
bob_results  = []


for i, base in enumerate(bob_bases):
    qc = eve_encoded_qubits[i].copy()  # Bob recibe los qubits interceptados por Eve
    if base == 'x':
        qc.h(0)  # Cambiar a base diagonal si Bob usa 'x'
    qc.measure(0, 0)  # Bob mide
    job = simulator.run(qc, noise_model=noise_model, shots=1)
    result = job.result()
    counts = result.get_counts(qc)
    bob_results.append(int(max(counts, key=counts.get)))

bob_measurements = np.array(bob_results)

# --- Paso 5: Reconciliación de claves ---
valid_indices = [i for i in range(num_qubits) if alice_bases[i] == bob_bases[i]]
alice_key = ''.join(str(alice_bits[i]) for i in valid_indices)
bob_key = ''.join(str(bob_measurements[i]) for i in valid_indices)

# --- Paso 6: Analizar el impacto de Eve ---
eve_valid_indices = [i for i in range(num_qubits) if alice_bases[i] == eve_bases[i]]
eve_key = ''.join(str(intercepted_results[i]) for i in valid_indices)

# --- Resultados ---
print("Bits de Alice:      ", ''.join(map(str, alice_bits)))
print("Bases de Alice:     ", ''.join(alice_bases))
print("Bases de Eve:       ", ''.join(eve_bases))
print("Bases de Bob:       ", ''.join(bob_bases))
print("Mediciones de Bob:  ", ''.join(map(str, bob_measurements)))
print("\nClaves reconciliadas:")
print("Clave de Alice:     ", alice_key)
print("Clave de Bob:       ", bob_key)
print("Coinciden (Alice-Bob):", alice_key == bob_key)
errores = sum(1 for a, b in zip(alice_key, bob_key) if a != b)
print("Fallos:", errores)
print("Porcentaje fallos:", (errores / len(bob_key)) * 100)
print("Clave de Eve:       ", eve_key)
print("Coinciden (Alice-Eve):", alice_key == eve_key)