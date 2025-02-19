from django.shortcuts import render
from django.http import JsonResponse
import os
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import json
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import Aer
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import depolarizing_error
import tensorflow as tf
from django.views.decorators.csrf import ensure_csrf_cookie
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64


def generate_ia_key(generator, num_qubits, latent_dim=256):
    latent_vectors = tf.random.normal((num_qubits, latent_dim))  # Generar ruido latente
    generated_sequences = generator.predict(latent_vectors)  # Generar secuencias
    sequence = np.round(generated_sequences).astype(int).flatten()  # Redondear a 0/1
    
    # Repetir o cortar para ajustarse a num_qubits
    return np.resize(sequence, num_qubits)

def show_qcircuits(request):
    if request.method == 'GET':

        possible_bits = [1,1,0,0]
        possible_bases = ['z', 'x', 'z', 'x']

        def show_circuits(bits, bases):
            circuits = []
            for bit, base in zip(bits, bases):
                qr = QuantumRegister(1, name="q")
                cr = ClassicalRegister(1, name="c")
                qc = QuantumCircuit(qr, cr)
                if bit == 1:
                    qc.x(qr[0])
                if base == 'x':
                    qc.h(qr[0])
                circuits.append((qc, bit, base))

            return circuits
        
        circuits = show_circuits(possible_bits, possible_bases)

         # Función para visualizar el circuito en base64
        def circuit_to_base64(qc):
            fig = qc.draw(output='mpl')  # Usar el formato MPL
            buf = BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()
            return img_base64
        
        imagesWithBases = []
        for qc, bit, base in circuits:
            img_base64 = circuit_to_base64(qc)
            imagesWithBases.append({
                'image': img_base64,
                'bit': bit,
                'base': base
            })
            
        return JsonResponse({
            'show_circuits': imagesWithBases
        })
    
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


def simulate(request):

    if request.method == 'POST':
        # Parsear la clave de Alice del frontend
        try:
            data = json.loads(request.body)
            use_interceptor = data.get("interceptor", False)
            alice_bits = np.array([int(bit) for bit in data.get('alice_bits', '')])
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid or missing alice_bits'}, status=400)

        if len(alice_bits) == 0:
            return JsonResponse({'error': 'alice_bits cannot be empty'}, status=400)

        num_qubits = len(alice_bits)
        alice_bases = np.random.choice(['z', 'x'], num_qubits)

        # Crear circuitos de Alice
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
        encoded_qubits = alice_qubits

        # Crear modelo de ruido
        noise_model = NoiseModel()
        depolarizing_prob = 0.05
        error = depolarizing_error(depolarizing_prob, 1)
        noise_model.add_all_qubit_quantum_error(error, ['id', 'u3', 'u2', 'u1', 'measure'])

        simulator = Aer.get_backend('qasm_simulator')

        if(use_interceptor):
            # Intercepción de Eve
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

        

        # Bob mide los qubits
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

        # Reconciliación de claves
        valid_indices = [i for i in range(num_qubits) if alice_bases[i] == bob_bases[i]]
        alice_key = ''.join(str(alice_bits[i]) for i in valid_indices)
        bob_key = ''.join(str(bob_measurements[i]) for i in valid_indices)
        errores = sum(1 for a, b in zip(alice_key, bob_key) if a != b)

        private_key_alice = alice_key[:16]
        private_key_bob = bob_key[:16]
        public_key_alice = alice_key[16:]
        public_key_bob = bob_key[16:]

        errores_public_key = sum(1 for a, b in zip(public_key_alice, public_key_bob) if a != b)

        qber = (errores / len(bob_key)) * 100

        qber_public_key = (errores_public_key / len(public_key_bob)) * 100

        # Resultados en JSON
        return JsonResponse({
            'alice_key': alice_key,
            'bob_key': bob_key,
            'alice_bits': ''.join(map(str, alice_bits)),
            'bob_measurements': ''.join(map(str, bob_measurements)),
            'qber': qber,
            'qber_public': qber_public_key,
            "private_key_alice": private_key_alice,
            "private_key_bob": private_key_bob,
            "public_key_alice": public_key_alice,
            "public_key_bob": public_key_bob
        })
    
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)
    

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({"message": "CSRF token set"})

def cascade_error_correction(alice_key, bob_key, block_size=4, rounds=3):
    """Corrige errores en la clave de Bob usando el método de cascada"""
    alice_key = np.array(list(map(int, alice_key)))
    bob_key = np.array(list(map(int, bob_key)))

    key_length = len(alice_key)

    for _ in range(rounds):
        indices = np.arange(key_length)
        np.random.shuffle(indices)  # Barajar los índices para cambiar la partición

        for i in range(0, key_length, block_size):
            block_indices = indices[i : i + block_size]
            if len(block_indices) < block_size:
                continue  # Saltar bloques incompletos

            # Calcular paridades
            alice_parity = alice_key[block_indices].sum() % 2
            bob_parity = bob_key[block_indices].sum() % 2

            if alice_parity != bob_parity:
                # Encontrar el bit erróneo usando búsqueda binaria
                low, high = 0, len(block_indices) - 1
                while low < high:
                    mid = (low + high) // 2
                    alice_sub_parity = alice_key[block_indices[low : mid+1]].sum() % 2
                    bob_sub_parity = bob_key[block_indices[low : mid+1]].sum() % 2

                    if alice_sub_parity != bob_sub_parity:
                        high = mid  # Error en la primera mitad
                    else:
                        low = mid + 1  # Error en la segunda mitad
                
                # Corregir el bit erróneo en Bob
                bob_key[block_indices[low]] ^= 1

    return "".join(map(str, bob_key))

def correct_key(request):
    if request.method == "POST":
        data = json.loads(request.body)
        alice_key = data.get("alice_key")
        bob_key = data.get("bob_key")

        corrected_key = cascade_error_correction(alice_key, bob_key)

        return JsonResponse({"corrected_key": corrected_key})

    return JsonResponse({"error": "Invalid request"}, status=400)

def xor_encrypt(message, key):
    """Cifra un mensaje usando XOR con la clave BB84"""
    
    encrypted = "".join(chr(ord(m) ^ ord(k)) for m, k in zip(message, key))
    return encrypted

def xor_decrypt(encrypted_message, key):
    """Descifra un mensaje XOR aplicando XOR nuevamente"""
    return xor_encrypt(encrypted_message, key)  

def encrypt(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get("message", "")
            key = data.get("key", "")
            

            if not message or not key:
                return JsonResponse({'error': 'Missing message or key'}, status=400)

            encrypted_data = xor_encrypt(message, key)
            return JsonResponse({"encrypted_message": encrypted_data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
def decrypt(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            key = data.get("key", "")
            encrypted_message = data.get("encrypted_message", "")

            if not key or not key:
                return JsonResponse({'error': 'Missing message or key'}, status=400)

            decrypted_message = xor_decrypt(key, encrypted_message)
            return JsonResponse({'message': decrypted_message})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
def encrypt_message(message, key):
    key = key[:16]
    cipher = AES.new(key.encode(), AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode()
    ct = base64.b64encode(ct_bytes).decode()
    return {"ciphertext": ct, "iv": iv}

def decrypt_message(ciphertext, key, iv):
    key = key[:16] 
    cipher = AES.new(key.encode(), AES.MODE_CBC, base64.b64decode(iv))
    pt = unpad(cipher.decrypt(base64.b64decode(ciphertext)), AES.block_size)
    return pt.decode()

def encryptAES(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get("message", "")
            key = data.get("key", "")

            if not message or not key:
                return JsonResponse({'error': 'Missing message or key'}, status=400)

            encrypted_data = encrypt_message(message, key)
            return JsonResponse(encrypted_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
def decryptAES(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ciphertext = data.get("encrypted_message", "")
            key = data.get("key", "")
            iv = data.get("iv", "")

            if not ciphertext or not key or not iv:
                return JsonResponse({'error': 'Missing ciphertext, key, or IV'}, status=400)

            decrypted_message = decrypt_message(ciphertext, key, iv)
            return JsonResponse({'message': decrypted_message})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
