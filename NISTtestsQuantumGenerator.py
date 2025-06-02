import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import Aer
import os

q_bits =100
shots = 150000

qreg_q = QuantumRegister(q_bits, 'q')
creg_c = ClassicalRegister(q_bits, 'c')
circuit = QuantumCircuit(qreg_q, creg_c)

for i in range(q_bits):
    circuit.h(qreg_q[i])
    circuit.measure(qreg_q[i], creg_c[i])

simulator = Aer.get_backend('qasm_simulator')
result = simulator.run(circuit, shots=shots).result()
counts = result.get_counts()

full_sequence = []
for bitstring, freq in counts.items():
    bits = list(map(int, bitstring[::-1]))
    for _ in range(freq):
        full_sequence.extend(bits)

bitstring_full = ''.join(map(str, full_sequence))

total_bits = q_bits * shots
print(f"Total bits generados: {len(bitstring_full)} (esperado: {total_bits})")

with open("quantum_sequence2", "w") as f:
    f.write(bitstring_full)

