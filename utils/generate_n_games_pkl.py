# Created by Andrew Silva on 3/29/18
import torchcraft
from torchcraft import replayer
import os
import pickle
import data_utils

unit_attrs = ['type', 'x', 'y', 'health', 'max_health', 'shield', 'max_shield', 'energy', 'maxCD', 'groundCD',
              'airCD', 'visible', 'type', 'armor', 'shieldArmor', 'size', 'pixel_x', 'pixel_y', 'pixel_size_x',
              'pixel_size_y', 'groundATK', 'airATK', 'groundDmgType', 'airDmgType', 'groundRange', 'airRange',
              'velocityX', 'velocityY', 'playerId', 'resources']
flags = ['accelerating', 'attacking', 'attack_frame', 'being_constructed', 'being_gathered', 'being_healed', 'blind', 'braking', 'burrowed', 'carrying_gas', 'carrying_minerals', 'cloaked', 'completed', 'constructing', 'defense_matrixed', 'detected', 'ensnared', 'flying', 'following', 'gathering_gas', 'gathering_minerals', 'hallucination', 'holding_position', 'idle', 'interruptible', 'invincible', 'irradiated', 'lifted', 'loaded', 'locked_down', 'maelstrommed', 'morphing', 'moving', 'parasited', 'patrolling', 'plagued', 'powered', 'repairing', 'researching', 'selected', 'sieged', 'starting_attack', 'stasised', 'stimmed', 'stuck', 'targetable', 'training', 'under_attack', 'under_dark_swarm', 'under_disruption_web', 'under_storm', 'upgrading']
# Uncomment for flags as attributes:
# unit_attrs += flags


# Currently not using flags (see above) or: Commands, crafted features (distance from start base, etc.)
def unit_to_dict(unit_in, add_orders=True):
    unit_dict = dict()
    unit_dict['type_name'] = data_utils.type_to_name(unit.type)
    for attribute in unit_attrs:
        unit_dict[attribute] = getattr(unit, attribute)
        if add_orders:
            order_list = []
            for order in unit_in.orders:
                order_list.append(order_to_dict(order))
            unit_dict['orders'] = order_list
    return unit_dict


def order_to_dict(order_in):
    order_dict = dict()
    order_dict['type'] = order_in.type
    order_dict['targetId'] = order_in.targetId
    order_dict['targetX'] = order_in.targetX
    order_dict['targetY'] = order_in.targetY
    return order_dict


def unit_to_arr(unit_in):
    unit_array = []
    for attribute in unit_attrs:
        unit_array.append(getattr(unit_in, attribute))
    label = unit_in.orders[-1].type
    if label == 133:
        if len(unit_in.orders) > 1:
            label = unit_in.orders[-2].type
    return [unit_array, label]


# This file is generated from `get_good_replays.py`
replays_master = open('good_files.txt', 'r').readlines()
for i in range(len(replays_master)):
    replays_master[i] = replays_master[i].split('\n')[0]


# this is how many games i'm going to save:
num_games_to_parse = 3
# Window size for action rec (in # frames, not in # sec):
window_size = 24
# counter to track how many i've saved:
counter = 0
# master list that will be pickled / saved:
game_list = []
# I only want information on these units [zergling, marine, scv, drone, probe, zealot]:
valid_types = [37, 0, 7, 41, 64, 65]
# loop over replay master list, grab first "num_games_to_parse"
for full_filename in replays_master:

    replay = replayer.load(full_filename)
    # TODO: Remove this hack eventually, but for now there is too much data in a 13k frame game looking at 6 unit types
    if len(replay) > 5500:
        continue

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

pickle_filename = str(num_games_to_parse)+"_games.pkl"
pickle.dump(game_list, open(pickle_filename, 'wb'))
print("Dump complete.")

# THIS IS OLD, SAVING IT FOR THE FUTURE POTENTIALLY:
# This saves everything in a temporally continuous way. So it watches a single unit over the course of it's life.
# Unfortunately, it's stupidly massive. I might want it later (or like..immediately), but for now I'm going to trim
# Down the size of my data by removing duplicates. Above code is for a much smaller / less repetitive dataset
# for full_filename in replays_master:
#
#     replay = replayer.load(full_filename)
#
#     if counter >= num_games_to_parse:
#         break
#     counter += 1
#
#     print("loaded replay: " + full_filename + " of length:" + str(len(replay)))
#     all_frames = []
#     # ids of units I care about:
#     units_i_want = {}
#     for frame_number in range(len(replay)):
#         frame = replay.getFrame(frame_number)
#         units = frame.units
#         this_frame = []
#         for player_id, unit_arr in units.iteritems():
#             if player_id < 0:
#                 # This is a map resource / object, not an army unit
#                 continue
#             # For each unit in this frame:
#             for unit in unit_arr:
#                 # Make sure it's a type that I care about
#                 if unit.type in valid_types:
#                     # If I already have it, append a new [state, label] to it, else add it to my dict
#                     if unit.id in units_i_want:
#                         units_i_want[unit.id].append(unit_to_arr(unit))
#                     else:
#                         units_i_want[unit.id] = [unit_to_arr(unit)]
#         # append list (frame) of lists (valid units) of [state, item] tuples to my gamewide list
#         all_frames.append(units_i_want.values())
#     # save gamewide list to all games
#     game_list.append(all_frames)
