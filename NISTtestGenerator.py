import tensorflow as tf
import numpy as np
generator = tf.keras.models.load_model('generator3.h5', compile=False)

latent_dim = 256
num_sequences = 468750
bits_per_sequence = 32
total_bits = num_sequences * bits_per_sequence

latent_vectors = tf.random.normal((num_sequences, latent_dim))
generated = generator.predict(latent_vectors).flatten()
generated = np.round(generated).astype(int)[:total_bits]
bitstring = ''.join(str(bit) for bit in generated)

with open("data2", "w") as f:
    f.write(bitstring)

print(f"Guardado {len(generated)} bits en el archivo 'data'")

