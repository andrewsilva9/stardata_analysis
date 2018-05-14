# Created by Andrew Silva on 5/14/18
from torchcraft import replayer
from keras.layers import Input, Dense, Flatten, Reshape, LSTM, RepeatVector
from keras.models import Model, load_model
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

    params = generate_role_datasets.hyper_params()

    data_path = '/home/asilva/Documents/stardata_analysis/deep_unsupervision/data/' + feature_set
    if add_orders:
        data_path += 'orders'
    data_path += '.pkl'
    if os.path.exists(data_path):
        X = cPickle.load(open(data_path, 'rb'))
    else:
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
    model_path = '/home/asilva/Documents/stardata_analysis/deep_unsupervision/models/' + str(latent_dim) + feature_set
    if add_orders:
        model_path += 'orders'
    model_path += '.h5'
    model = load_model(model_path)
    get_output = K.function([model.layers[0].input],
                            [model.layers[1].output])
    all_embeds = get_output([X])[0]

    # Save the data
    data_path = '/home/asilva/Documents/stardata_analysis/deep_unsupervision/data/' + feature_set
    if add_orders:
        data_path += 'orders'
    data_path += '.pkl'
    cPickle.dump(X, open(data_path, 'wb'), protocol=cPickle.HIGHEST_PROTOCOL)

    # Save the embeds
    embed_path = '/home/asilva/Documents/stardata_analysis/deep_unsupervision/embeds/' + str(latent_dim) + feature_set
    if add_orders:
        embed_path += 'orders'
    embed_path += '.pkl'
    cPickle.dump(all_embeds, open(embed_path, 'wb'), protocol=cPickle.HIGHEST_PROTOCOL)
