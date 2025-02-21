import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LeakyReLU, BatchNormalization, Dropout, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import BinaryCrossentropy
from tensorflow.keras.models import Model

num_samples = 5000
seq_length = 32
latent_dim = 256
batch_size = 64
epochs = 50  # Más entrenamiento

def generate_balanced_sequences(num_samples, seq_length):
    dataset = np.random.choice([0, 1], size=(num_samples, seq_length))  
    return dataset

dataset = generate_balanced_sequences(num_samples, seq_length)
tf_dataset = tf.data.Dataset.from_tensor_slices(dataset).batch(batch_size).cache().prefetch(tf.data.AUTOTUNE)


plt.figure(figsize=(10, 6))
for i in range(5):  # Visualizar 5 secuencias
    plt.subplot(5, 1, i + 1)
    plt.plot(dataset[i])
    plt.title(f"Secuencia {i+1}")
plt.tight_layout()
plt.show()

print("Secuencia Generada (redondeada):", dataset[1])


def build_generator(latent_dim, seq_length):
    model = Sequential()
    model.add(Dense(256, input_dim=latent_dim))  # Más unidades iniciales
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.2))

    model.add(Dense(512))  # Incrementar gradualmente
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.2))
    model.add(Dropout(0.3))

    model.add(Dense(256))  # Reducir hacia la salida
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.2))

    model.add(Dense(seq_length, activation='sigmoid'))  # Salida final
    return model

# Crear modelos
generator = build_generator(latent_dim, seq_length)

generator.summary()

seq = generator.predict(np.random.normal(0, 1, (1, latent_dim)))
binary_sequence = (seq > 0.5).astype(int)
# Visualizar la secuencia
plt.figure(figsize=(10, 1))
plt.imshow(binary_sequence, cmap="binary", aspect="auto")
plt.title("Secuencia Generada")
plt.xlabel("Índice de la Secuencia")
plt.ylabel("Valor")
plt.colorbar(label="0 o 1")
plt.show()

# Imprimir la secuencia generada
print("Secuencia Generada (redondeada):", binary_sequence.flatten())




# Discriminador
def build_discriminator(seq_length):

    model = Sequential()
    model.add(Input(shape=(seq_length,)))  # Entrada con tamaño de la secuencia
    model.add(Dense(256))                 
    model.add(LeakyReLU(0.2))             
    model.add(Dropout(0.3))   
    
    model.add(Dense(128))                
    model.add(LeakyReLU(0.2))             
    model.add(Dropout(0.3))             

    model.add(Dense(64))                  # Reducir el tamaño
    model.add(LeakyReLU(0.2))

    model.add(Dense(1, activation="sigmoid"))  # Salida binaria (real o falso)
    return model

discriminator = build_discriminator(seq_length)

# discriminator.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0002), loss="binary_crossentropy", metrics=["accuracy"])
# discriminator.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

discriminator.summary()


discriminator.predict(seq)



g_opt = Adam(learning_rate=0.0001)  
d_opt = Adam(learning_rate=0.00005)  

g_loss = BinaryCrossentropy()
d_loss = BinaryCrossentropy()
tf.random.normal(())


class RandomGAN(Model):
  def __init__(self, generator, discriminator, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator = generator
    self.discriminator = discriminator

  def compile(self, g_opt, d_opt, g_loss, d_loss, *args, **kwargs):
    super().compile(*args, **kwargs)

    self.g_opt = g_opt
    self.d_opt = d_opt
    self.g_loss = g_loss
    self.d_loss = d_loss

  def train_step(self, batch):
    real_sequences = batch
    batch_size = tf.shape(real_sequences)[0]

    random_latent_vectors = tf.random.normal((batch_size, latent_dim))
    fake_sequences = self.generator(random_latent_vectors, training=False)

    with tf.GradientTape() as d_tape:

            # Predicciones para datos reales y falsos
            yhat_real = self.discriminator(real_sequences, training=True)
            yhat_fake = self.discriminator(fake_sequences, training=True)
            yhat_realfake = tf.concat([yhat_real, yhat_fake], axis=0)

            # Etiquetas para datos reales y falsos
            y_realfake = tf.concat([tf.ones_like(yhat_real), tf.zeros_like(yhat_fake)], axis=0)


            # Pérdida del discriminador
            total_d_loss = self.d_loss(y_realfake, yhat_realfake)

    d_gradients = d_tape.gradient(total_d_loss, self.discriminator.trainable_variables)
    self.d_opt.apply_gradients(zip(d_gradients, self.discriminator.trainable_variables))


    with tf.GradientTape() as g_tape:
            # Generar secuencias
            gen_sequences = self.generator(random_latent_vectors, training=True)

            # Predicciones del discriminador para datos generados
            predicted_labels = self.discriminator(gen_sequences, training=False)

            # Pérdida del generador (queremos que el discriminador los clasifique como reales)
            total_g_loss = self.g_loss(tf.ones_like(predicted_labels), predicted_labels)

    # Actualizar los pesos del generador
    g_gradients = g_tape.gradient(total_g_loss, self.generator.trainable_variables)
    self.g_opt.apply_gradients(zip(g_gradients, self.generator.trainable_variables))

    # 5. Retornar pérdidas para seguimiento
    return {"d_loss": total_d_loss, "g_loss": total_g_loss}


randomgan = RandomGAN(generator, discriminator)

randomgan.compile(g_opt, d_opt, g_loss, d_loss)

hist = randomgan.fit(tf_dataset, epochs=500)

plt.suptitle('Loss')
plt.plot(hist.history['d_loss'], label='d_loss')
plt.plot(hist.history['g_loss'], label='g_loss')
plt.legend()
plt.show()

generator.save('generator.h5')
discriminator.save('discriminator.h5')
