# Created by Andrew Silva on 4/6/18
# This file will generate matrices of games, where a unit is a document and an order is a word
# We will consider orders every N seconds, with N beginning at 1/8 and incrementing to... 2 sec?
# Created by Andrew Silva on 3/29/18
import torchcraft
from torchcraft import replayer
import os
import numpy as np
import pickle
import data_utils

# max speed is 8 fps, so 1/8 seconds is fastest we can do. 8/8 is 1 second, 16/8 is 2, etc...
N_secs = 16/8.0
# I only want information on these units [zergling, marine, scv, drone, probe, zealot]:
valid_types = np.arange(0, 250)

# This file is generated from `get_good_replays.py`
replays_master = open('good_files.txt', 'r').readlines()
for i in range(len(replays_master)):
    replays_master[i] = replays_master[i].split('\n')[0]

# counter to track how many i've saved:
counter = 0

# number of games to include for this dataset
num_games_to_parse = 1


def get_orders(unit_in):
    orders = []
    for order in unit_in.orders:
        orders.append(order.type)
    return orders


# master list of games
game_list = None

for full_filename in replays_master:

    replay = replayer.load(full_filename)

    if counter >= num_games_to_parse:
        break
    counter += 1

    print("loaded replay: " + full_filename + " of length:" + str(len(replay)))
    # ids of units I care about:
    units_i_want = {}
    for frame_number in range(0, len(replay), int(N_secs*8)):
        frame = replay.getFrame(frame_number)
        units = frame.units
        this_frame = []
        for player_id, unit_arr in units.iteritems():
            if player_id < 0:
                # This is a map resource / object, not an army unit
                continue
            # For each unit in this frame:
            for unit in unit_arr:
                # Make sure it's a type that I care about
                if unit.type in valid_types:
                    # If I already have it, append a new [state, label] to it, else add it to my dict
                    if unit.id in units_i_want:
                        for val in get_orders(unit):
                            units_i_want[unit.id][val] += 1
                    else:
                        units_i_want[unit.id] = np.zeros(len(data_utils.order_enum))
        # append list (frame) of lists (valid units) of [state, item] tuples to my gamewide list
    # save gamewide list to all games
    if game_list is None:
        game_list = np.array(units_i_want.values())
    else:
        game_list = np.concatenate((game_list, np.array(units_i_want.values())), axis=0)
pickle_filename = str(num_games_to_parse)+"_lda_games.pkl"
pickle.dump(game_list, open(pickle_filename, 'wb'))
print("Dump complete.")