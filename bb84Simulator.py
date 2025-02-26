import os
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import Aer
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import depolarizing_error
import numpy as np
import tensorflow as tf

latent_dim = 256
seq_length = 32

generator = tf.keras.models.load_model('generator3.h5', compile=False)

def generate_ia_key(generator, num_qubits, latent_dim=256):
    latent_vectors = tf.random.normal((num_qubits, latent_dim))  
    generated_sequences = generator.predict(latent_vectors)  
    sequence = np.round(generated_sequences).astype(int).flatten()  
    
    return np.resize(sequence, num_qubits)


num_qubits = 200
alice_bits = generate_ia_key(generator, num_qubits, latent_dim)  
alice_bases = np.random.choice(['z', 'x'], num_qubits)  


def encode_qubits(bits, bases):
    circuits = []
    for bit, base in zip(bits, bases):
        qr = QuantumRegister(1, name="q")
        cr = ClassicalRegister(1, name="c")
        qc = QuantumCircuit(qr, cr)
        
        if bit == 1:
            qc.x(qr[0])  
        if base == 'x':
            qc.h(qr[0])  
            
        circuits.append(qc)
    return circuits

alice_qubits = encode_qubits(alice_bits, alice_bases)


noise_model = NoiseModel()
depolarizing_prob = 0.05  
error = depolarizing_error(depolarizing_prob, 1)  
noise_model.add_all_qubit_quantum_error(error, ['id', 'u3', 'u2', 'u1', 'measure'])

eve_bases = np.random.choice(['z', 'x'], num_qubits) 
intercepted_results = []

simulator = Aer.get_backend('qasm_simulator')

for i, base in enumerate(eve_bases):
    qc = alice_qubits[i].copy()  
    if base == 'x':
        qc.h(0)  
    qc.measure(0, 0)  
    job = simulator.run(qc, noise_model=noise_model, shots=1)
    result = job.result()
    counts = result.get_counts(qc)
    intercepted_results.append(int(max(counts, key=counts.get)))

eve_encoded_qubits = encode_qubits(intercepted_results, eve_bases)

bob_bases = np.random.choice(['z', 'x'], num_qubits)
bob_results  = []


for i, base in enumerate(bob_bases):
    qc = eve_encoded_qubits[i].copy() 
    if base == 'x':
        qc.h(0)  
    qc.measure(0, 0)  
    job = simulator.run(qc, noise_model=noise_model, shots=1)
    result = job.result()
    counts = result.get_counts(qc)
    bob_results.append(int(max(counts, key=counts.get)))

bob_measurements = np.array(bob_results)

valid_indices = [i for i in range(num_qubits) if alice_bases[i] == bob_bases[i]]
alice_key = ''.join(str(alice_bits[i]) for i in valid_indices)
bob_key = ''.join(str(bob_measurements[i]) for i in valid_indices)

eve_valid_indices = [i for i in range(num_qubits) if alice_bases[i] == eve_bases[i]]
eve_key = ''.join(str(intercepted_results[i]) for i in valid_indices)

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