import os
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import Aer
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import depolarizing_error
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

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

fallos_porcentuales = []

# Ejecutar la simulación 100 veces
for _ in range(100):
    alice_bits = generate_ia_key(generator, num_qubits, latent_dim)
    alice_bases = np.random.choice(['z', 'x'], num_qubits)
    alice_qubits = encode_qubits(alice_bits, alice_bases)

    eve_bases = np.random.choice(['z', 'x'], num_qubits)
    intercepted_results = []

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
    bob_results = []

    for i, base in enumerate(bob_bases):
        qc = alice_qubits[i].copy()
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

    errores = sum(1 for a, b in zip(alice_key, bob_key) if a != b)
    if len(bob_key) > 0:
        porcentaje_error = (errores / len(bob_key)) * 100
        fallos_porcentuales.append(porcentaje_error)

# 📊 Visualización de los resultados
plt.figure(figsize=(10, 5))
plt.plot(fallos_porcentuales, marker='o', linestyle='-', color='red', label="Porcentaje de fallos")
plt.title("Evolución del porcentaje de fallos entre Alice y Bob (100 ejecuciones)")
plt.xlabel("Ejecución")
plt.ylabel("Porcentaje de fallos (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

def simulation(bits, use_interceptor):
        num_qubits = len(bits)
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

        alice_qubits = encode_qubits(bits, alice_bases)
        encoded_qubits = alice_qubits

        noise_model = NoiseModel()
        depolarizing_prob = 0.05
        error = depolarizing_error(depolarizing_prob, 1)
        noise_model.add_all_qubit_quantum_error(error, ['id', 'u3', 'u2', 'u1', 'measure'])

        simulator = Aer.get_backend('qasm_simulator')

        if(use_interceptor):
            eve_bases = np.random.choice(['z', 'x'], num_qubits)
            intercepted_results = []

            for i, base in enumerate(eve_bases):
                qc = alice_qubits[i].copy()
                if base == 'x':
                    qc.h(0)
                qc.measure(0, 0)
                job = simulator.run(qc, noise_model=noise_model, shots=1)
                result = job.result()
                counts = result.get_counts(qc)
                intercepted_results.append(int(max(counts, key=counts.get)))

            encoded_qubits = encode_qubits(intercepted_results, eve_bases)

        
        bob_bases = np.random.choice(['z', 'x'], num_qubits)
        bob_results = []

        for i, base in enumerate(bob_bases):
            qc = encoded_qubits[i].copy()
            if base == 'x':
                qc.h(0)
            qc.measure(0, 0)
            job = simulator.run(qc, noise_model=noise_model, shots=1)
            result = job.result()
            counts = result.get_counts(qc)
            bob_results.append(int(max(counts, key=counts.get)))

        bob_measurements = np.array(bob_results)

        valid_indices = [i for i in range(num_qubits) if alice_bases[i] == bob_bases[i]]
        alice_key = ''.join(str(bits[i]) for i in valid_indices)
        bob_key = ''.join(str(bob_measurements[i]) for i in valid_indices)
        errores = sum(1 for a, b in zip(alice_key, bob_key) if a != b)

        private_key_alice = alice_key[:16]
        private_key_bob = bob_key[:16]
        public_key_alice = alice_key[16:]
        public_key_bob = bob_key[16:]

        errores_public_key = sum(1 for a, b in zip(public_key_alice, public_key_bob) if a != b)

        qber = (errores / len(bob_key)) * 100

        qber_public_key = (errores_public_key / len(public_key_bob)) * 100

        return {"alice_bits": bits, "alice_bases": alice_bases, "bob_bases": bob_bases, "bob_measurements": bob_measurements,
                "alice_key": alice_key, "bob_key": bob_key, "private_key_alice": private_key_alice, "private_key_bob": private_key_bob, 
                "qber": qber, "qber_public": qber_public_key
                }