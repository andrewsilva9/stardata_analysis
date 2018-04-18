# Created by Andrew Silva on 3/29/18
import torchcraft
from torchcraft import replayer
import os
import pickle
import numpy as np
import data_utils

unit_attrs = ['type', 'x', 'y', 'health', 'max_health', 'shield', 'max_shield', 'energy', 'maxCD', 'groundCD',
              'airCD', 'visible', 'armor', 'shieldArmor', 'size', 'pixel_x', 'pixel_y', 'pixel_size_x',
              'pixel_size_y', 'groundATK', 'airATK', 'groundDmgType', 'airDmgType', 'groundRange', 'airRange',
              'velocityX', 'velocityY', 'playerId', 'resources']
flags = ['accelerating', 'attacking', 'attack_frame', 'being_constructed', 'being_gathered', 'being_healed', 'blind', 'braking', 'burrowed', 'carrying_gas', 'carrying_minerals', 'cloaked', 'completed', 'constructing', 'defense_matrixed', 'detected', 'ensnared', 'flying', 'following', 'gathering_gas', 'gathering_minerals', 'hallucination', 'holding_position', 'idle', 'interruptible', 'invincible', 'irradiated', 'lifted', 'loaded', 'locked_down', 'maelstrommed', 'morphing', 'moving', 'parasited', 'patrolling', 'plagued', 'powered', 'repairing', 'researching', 'selected', 'sieged', 'starting_attack', 'stasised', 'stimmed', 'stuck', 'targetable', 'training', 'under_attack', 'under_dark_swarm', 'under_disruption_web', 'under_storm', 'upgrading']
# Uncomment for flags as attributes:
# unit_attrs += flags


# Currently not using flags (see above) or: Commands, crafted features (distance from start base, etc.)
def unit_to_dict(unit_in, add_orders=True):
    """
    convert a unit to a dictionary of all attributes
    :param unit_in: unit to interpret
    :param add_orders: should i add orders to the dict?
    :return: dictionary of {key: value} for all keys in unit_attrs global
    """
    unit_dict = dict()
    unit_dict['type_name'] = data_utils.type_to_name(unit_in.type)
    for attribute in unit_attrs:
        unit_dict[attribute] = getattr(unit_in, attribute)
        if add_orders:
            order_list = []
            for order in unit_in.orders:
                order_list.append(order_to_dict(order))
            unit_dict['orders'] = order_list
    return unit_dict


def order_to_dict(order_in):
    """
    transform an order into a dict of attributes and values
    :param order_in: order to interpret
    :return: dict of {type:type, targetId:target, targetX:target, targetY:target}
    """
    order_dict = dict()
    order_dict['type'] = order_in.type
    order_dict['targetId'] = order_in.targetId
    order_dict['targetX'] = order_in.targetX
    order_dict['targetY'] = order_in.targetY
    return order_dict


def unit_to_arr(unit_in):
    """
    transform a unit into an (attributes, order) tuple
    :param unit_in: unit to gather info on
    :return: (attributes, order) tuple
    """
    unit_array = []
    for attribute in unit_attrs:
        unit_array.append(getattr(unit_in, attribute))
    label = unit_in.orders[-1].type
    if label == 133:
        if len(unit_in.orders) > 1:
            label = unit_in.orders[-2].type
    return [unit_array, label]


def unit_to_np(unit_in):
    """
    use unit_to_arr to get a np array of unit data
    :param unit_in: unit to turn into np array
    :return: np array of all unit data + their current order
    """
    unit_data, label = unit_to_arr(unit_in)
    unit_data.append(label)
    return np.array(unit_data)


def get_nearest_units(unit_in, all_units, threshold=200, n_nearest=1):
    """
    return a np array of self + nearest n_nearest units
    :param unit_in: unit to compare to
    :param all_units: all units owned by the same player
    :param threshold: must be at least this close
    :param n_nearest: how many neighbors to return
    :return: 2d np array of [units, attributes]
    """
    distances = []
    candidates = None
    invalid_types = [13, 14, 15] # [spider mine, nuke, civilian??(not even a combat unit?)]
    for unit in all_units:
        if unit.id == unit_in.id:
            continue
        # If unit is not a valid unit (buildings are > 103)
        if unit.type in invalid_types or unit.type > 103:
            continue
        #TODO: make sure i'm not comparing to a building...
        x_diff = abs(unit.pixel_x - unit_in.pixel_x)
        y_diff = abs(unit.pixel_y - unit_in.pixel_y)
        if x_diff > threshold or y_diff > threshold:
            continue
        distances.append(np.sqrt(x_diff**2+y_diff**2))
        if candidates is None:
            candidates = unit_to_np(unit)
        else:
            candidates = np.vstack((candidates, unit_to_np(unit)))
    # there are 30 dimensions per unit
    if candidates is None:
        return np.zeros((n_nearest, 30))
    elif len(distances) <= n_nearest:
        shape_mod = n_nearest + 1 - len(distances)
        candidates = np.vstack((candidates, np.zeros((shape_mod, 30))))
        distances = distances + [max(distances)+1]*shape_mod
    distances = np.array(distances)
    nearest = np.argpartition(distances, n_nearest)
    return candidates[nearest[:n_nearest]]

# This file is generated from `get_good_replays.py`
replays_master = open('good_files.txt', 'r').readlines()
for i in range(len(replays_master)):
    replays_master[i] = replays_master[i].split('\n')[0]


def get_temporal_replays():
    step_size = 8  # 1 frame per second if step size = 8

    for full_filename in replays_master:

        replay = replayer.load(full_filename)

        print("loaded replay: " + full_filename + " of length:" + str(len(replay)))
        units_over_time = {}
        for frame_number in range(0, len(replay), step_size):
            frame = replay.getFrame(frame_number)
            units = frame.units
            for player_id, unit_arr in units.iteritems():
                if player_id < 0:
                    # This is a map resource / object, not an army unit
                    continue
                # For each unit in this frame:
                for unit in unit_arr:
                    # Make sure it's a type that I care about
                    if unit.type in valid_types:
                        # get nearest neighbors
                        neighbors = get_nearest_units(unit, unit_arr, threshold=200, n_nearest=11)
                        # create matrix with me at top, my neighbors under me
                        unit_and_neighbors = np.vstack((unit_to_np(unit), neighbors))
                        if unit.id in units_over_time:
                            units_over_time[unit.id].append(unit_and_neighbors)
                        else:
                            units_over_time[unit.id] = [unit_and_neighbors]
                # End iteration over units for player_id in this frame
            # End iteration over units for all players in this frame
        new_fn = '/media/asilva/HD_home/my_sc_data/temporal_pickles/' + full_filename.split('/')[-1] + '.pkl'
        pickle.dump(units_over_time, open(new_fn, 'wb'))
        print('dumped to ' + new_fn)
        # End iteration over all frames
    return True


def get_unique_unit_replay():
    game_list = []
    counter = 0
    # loop over replay master list, grab first "num_games_to_parse"
    for full_filename in replays_master:

        replay = replayer.load(full_filename)

        if counter >= num_games_to_parse:
            break
        counter += 1

        print("loaded replay: " + full_filename + " of length:" + str(len(replay)))
        # ids of units I care about:
        for frame_number in range(len(replay)):
            frame = replay.getFrame(frame_number)
            units = frame.units
            for player_id, unit_arr in units.iteritems():
                if player_id < 0:
                    # This is a map resource / object, not an army unit
                    continue
                # For each unit in this frame:
                for unit in unit_arr:
                    # Make sure it's a type that I care about
                    if unit.type in valid_types:
                        unit_data_arr = unit_to_arr(unit)
                        # Don't add if I already have this exact state/label combo
                        if (unit_data_arr in game_list) or (unit_data_arr[1] == 133):
                            continue
                        else:
                            game_list.append(unit_data_arr)
    return game_list


if __name__ == '__main__':

    # this is how many games i'm going to save:
    num_games_to_parse = 3
    # I only want information on these units [zergling, marine, scv, drone, probe, zealot]:
    valid_types = [37, 0, 7, 41, 64, 65]

    temporal = True
    if temporal:
        final_data = get_temporal_replays()
    else:
        final_data = get_unique_unit_replay()

    pickle_filename = str(num_games_to_parse)+"_games.pkl"
    pickle.dump(final_data, open(pickle_filename, 'wb'))
    print("Dump complete.")
