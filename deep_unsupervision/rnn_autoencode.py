from torchcraft import replayer
from keras.layers import Input, Dense, Flatten, Reshape, LSTM, RepeatVector
from keras.models import Model
from keras import backend as K
from keras.callbacks import TensorBoard
import numpy as np
import matplotlib.pyplot as plt
import cPickle
import sys
import argparse
import os
import h5py
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session

sys.path.insert(0, os.path.abspath('..'))
from utils import data_utils, generate_role_datasets


if __name__ == "__main__":
    # python rnn_autoencode.py args:
    # <NUM_GAMES int>,
    # <FEATURE_SET, "min", "med", "max">,
    # <ADD_ORDERS, True, False>,
    # <LATENT_DIM int>
    parser = argparse.ArgumentParser()
    parser.add_argument('--latent_dim', '-l', help="embedding dimension for autoencoder", type=int, default=16)
    parser.add_argument('--add_orders', '-o', help="add order feature (int bool)", type=int, default=0)
    parser.add_argument('--feature_set', '-f', help="which feature set to use", type=str, default="max")
    parser.add_argument('--num_games', '-n', help="number of games to get features from", type=int, default=10)
    #
    # latent_dim = 16
    # add_orders = True
    # feature_set = 'max'
    # num_games = 25
    # if len(sys.argv) > 4:
    #     latent_dim = sys.argv[4]
    # if len(sys.argv) > 3:
    #     add_orders = sys.argv[3]
    # if len(sys.argv) > 2:
    #     feature_set = sys.argv[2]
    # if len(sys.argv) > 1:
    #     num_games = sys.argv[1]
    args = parser.parse_args()
    latent_dim = args.latent_dim
    add_orders = args.add_orders
    feature_set = args.feature_set
    num_games = args.num_games
    print("latent_dim: " + str(latent_dim))
    print("Add orders?: " + str(bool(add_orders)))
    print("Features: " + feature_set)
    print("Num games?: " + str(num_games))
    #
    params = generate_role_datasets.hyper_params()
    data_replays = params['replays_master']
    X = data_utils.autoencode_dataset(data_replays,
                                      valid_types=params['valid_units'],
                                      step_size=1,
                                      window_size=params['window_size'],
                                      feature_set=feature_set,
                                      add_orders=add_orders,
                                      num_games=num_games)

    config = tf.ConfigProto()
    config.gpu_options.per_process_gpu_memory_fraction = 0.1
    set_session(tf.Session(config=config))
    input_dim = len(X[0][0])
    inputs = Input(shape=(params['window_size'], input_dim))
    encoded = LSTM(latent_dim, name='lstm_layer')(inputs)

    decoded = RepeatVector(params['window_size'])(encoded)

    decoded = LSTM(input_dim, return_sequences=True)(decoded)

    autoencoder = Model(inputs, decoded)
    autoencoder.compile(optimizer='adam', loss='mean_squared_error')
    len90 = int(len(X)*0.9)
    x_train = X[:len90]
    x_test = X[len90:]
    autoencoder.fit(x_train, x_train,
                    epochs=50,
                    batch_size=32,
                    shuffle=True,
                    validation_data=(x_test, x_test))
    # Save the model
    model_path = '/home/asilva/Documents/stardata_analysis/deep_unsupervision/models/' + str(latent_dim) + feature_set
    if add_orders:
        model_path += 'orders'
    model_path += '.h5'
    autoencoder.save(model_path)
    # Save the data
    pickle_path = '/home/asilva/Documents/stardata_analysis/deep_unsupervision/data/' + feature_set
    if add_orders:
        pickle_path += 'orders'
    pickle_path += '.pkl'
    cPickle.dump(X, open(pickle_path, 'wb'), protocol=cPickle.HIGHEST_PROTOCOL)
