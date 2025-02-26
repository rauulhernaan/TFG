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
epochs = 50

def generate_balanced_sequences(num_samples, seq_length):
    dataset = np.random.choice([0, 1], size=(num_samples, seq_length))  
    return dataset

dataset = generate_balanced_sequences(num_samples, seq_length)
tf_dataset = tf.data.Dataset.from_tensor_slices(dataset).batch(batch_size).cache().prefetch(tf.data.AUTOTUNE)


plt.figure(figsize=(10, 6))
for i in range(5):
    plt.subplot(5, 1, i + 1)
    plt.plot(dataset[i])
    plt.title(f"Secuencia {i+1}")
plt.tight_layout()
plt.show()

print("Secuencia Generada (redondeada):", dataset[1])


def build_generator(latent_dim, seq_length):
    model = Sequential()
    model.add(Dense(256, input_dim=latent_dim))
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.2))

    model.add(Dense(512))
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.2))
    model.add(Dropout(0.3))

    model.add(Dense(256))
    model.add(BatchNormalization())
    model.add(LeakyReLU(0.2))

    model.add(Dense(seq_length, activation='sigmoid'))
    return model

generator = build_generator(latent_dim, seq_length)

generator.summary()

seq = generator.predict(np.random.normal(0, 1, (1, latent_dim)))
binary_sequence = (seq > 0.5).astype(int)
plt.figure(figsize=(10, 1))
plt.imshow(binary_sequence, cmap="binary", aspect="auto")
plt.title("Secuencia Generada")
plt.xlabel("Índice de la Secuencia")
plt.ylabel("Valor")
plt.colorbar(label="0 o 1")
plt.show()

print("Secuencia Generada (redondeada):", binary_sequence.flatten())


def build_discriminator(seq_length):

    model = Sequential()
    model.add(Input(shape=(seq_length,)))
    model.add(Dense(256))                 
    model.add(LeakyReLU(0.2))             
    model.add(Dropout(0.3))   
    
    model.add(Dense(128))                
    model.add(LeakyReLU(0.2))             
    model.add(Dropout(0.3))             

    model.add(Dense(64))               
    model.add(LeakyReLU(0.2))

    model.add(Dense(1, activation="sigmoid")) 
    return model

discriminator = build_discriminator(seq_length)

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

            yhat_real = self.discriminator(real_sequences, training=True)
            yhat_fake = self.discriminator(fake_sequences, training=True)
            yhat_realfake = tf.concat([yhat_real, yhat_fake], axis=0)

            y_realfake = tf.concat([tf.ones_like(yhat_real), tf.zeros_like(yhat_fake)], axis=0)


            total_d_loss = self.d_loss(y_realfake, yhat_realfake)

    d_gradients = d_tape.gradient(total_d_loss, self.discriminator.trainable_variables)
    self.d_opt.apply_gradients(zip(d_gradients, self.discriminator.trainable_variables))


    with tf.GradientTape() as g_tape:
            gen_sequences = self.generator(random_latent_vectors, training=True)

            predicted_labels = self.discriminator(gen_sequences, training=False)

            total_g_loss = self.g_loss(tf.ones_like(predicted_labels), predicted_labels)

    g_gradients = g_tape.gradient(total_g_loss, self.generator.trainable_variables)
    self.g_opt.apply_gradients(zip(g_gradients, self.generator.trainable_variables))

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
