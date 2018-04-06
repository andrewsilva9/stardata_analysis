# Created by Andrew Silva on 4/6/18
from keras.layers import Input, Dense, Conv2D, MaxPooling2D, UpSampling2D, Flatten, Reshape
from keras.models import Model
from keras import backend as K
from keras.datasets import mnist
from keras.callbacks import TensorBoard

import numpy as np

import matplotlib.pyplot as plt

input_img = Input(shape=(28, 28, 1))

x = Conv2D(16,
           (3, 3),
           activation='tanh',
           padding='same')(input_img)
x = MaxPooling2D((2, 2),
                 padding='same')(x)
x = Conv2D(8,
           (3, 3),
           activation='tanh',
           padding='same')(x)
x = MaxPooling2D((2, 2),
                 padding='same')(x)
x = Flatten()(x)
x = Dense(256)(x)

encoded = Dense(100)(x)


# at this point the representation is (4, 4, 8) i.e. 128-dimensional

x = Dense(100)(encoded)
x = Dense(256)(x)
x = Reshape((8, 8, 4))(x)
x = Conv2D(8,
           (3, 3),
           activation='tanh',
           padding='same')(x)
x = UpSampling2D((2, 2))(x)
x = Conv2D(16,
           (3, 3),
           activation='tanh')(x)
x = UpSampling2D((2, 2))(x)
decoded = Conv2D(1,
                 (1, 1),
                 activation='sigmoid',
                 padding='same',
                 name='output_layer')(x)

autoencoder = Model(input_img, decoded)
autoencoder.compile(optimizer='adadelta',
                    loss='binary_crossentropy')

(x_train, _), (x_test, _) = mnist.load_data()
x_train = x_train.astype('float32') / 255.
x_test = x_test.astype('float32') / 255.
x_train = np.reshape(x_train, (len(x_train), 28, 28, 1))
x_test = np.reshape(x_test, (len(x_test), 28, 28, 1))

autoencoder.fit(x_train, x_train,
                epochs=50,
                batch_size=128,
                shuffle=True,
                validation_data=(x_test, x_test),
                callbacks=[TensorBoard(log_dir='/tmp/autoencoder')])

decoded_imgs = autoencoder.predict(x_test)

n = 10
plt.figure(figsize=(20, 4))
for i in range(1, n):
    # display original
    ax = plt.subplot(2, n, i)
    plt.imshow(x_test[i].reshape(28, 28))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # display reconstruction
    ax = plt.subplot(2, n, i + n)
    plt.imshow(decoded_imgs[i].reshape(28, 28))
    plt.gray()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
plt.show()
