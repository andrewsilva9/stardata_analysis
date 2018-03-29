# Created by Andrew Silva on 3/29/18
import torchcraft
from torchcraft import replayer
import os
import pickle
import data_utils

# Set this to the directory where you have the StarData replays
dumped_replays = '/media/asilva/HD_home/StarData/dumped_replays/'

unit_attrs = ['type', 'x', 'y', 'health', 'max_health', 'shield', 'max_shield', 'energy', 'maxCD', 'groundCD',
              'airCD', 'visible', 'type', 'armor', 'shieldArmor', 'size', 'pixel_x', 'pixel_y', 'pixel_size_x',
              'pixel_size_y', 'groundATK', 'airATK', 'groundDmgType', 'airDmgType', 'groundRange', 'airRange',
              'velocityX', 'velocityY', 'playerId', 'resources']
flags = ['accelerating', 'attacking', 'attack_frame', 'being_constructed', 'being_gathered', 'being_healed', 'blind', 'braking', 'burrowed', 'carrying_gas', 'carrying_minerals', 'cloaked', 'completed', 'constructing', 'defense_matrixed', 'detected', 'ensnared', 'flying', 'following', 'gathering_gas', 'gathering_minerals', 'hallucination', 'holding_position', 'idle', 'interruptible', 'invincible', 'irradiated', 'lifted', 'loaded', 'locked_down', 'maelstrommed', 'morphing', 'moving', 'parasited', 'patrolling', 'plagued', 'powered', 'repairing', 'researching', 'selected', 'sieged', 'starting_attack', 'stasised', 'stimmed', 'stuck', 'targetable', 'training', 'under_attack', 'under_dark_swarm', 'under_disruption_web', 'under_storm', 'upgrading']
# Uncomment for flags as attributes:
# unit_attrs += flags


# Currently not using flags (see above) or: Commands, crafted features (distance from start base, etc.)
def unit_to_dict(unit_in, add_orders=True):
    unit_dict = {}
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


replay_dirs = []
# Get all subdirectories inside the dumped_replays master directory
for contents in os.listdir(dumped_replays):
    full_path = os.path.join(dumped_replays, contents)
    if os.path.isdir(full_path):
        replay_dirs.append(full_path)

replays_master = []
# aggregate full paths to all replays in one master list
for replay_dir in replay_dirs:
    for replay in os.listdir(replay_dir):
        if replay.endswith('.tcr'):
            replays_master.append(os.path.join(replay_dir, replay))

# this is how many games i'm going to save:
num_games_to_parse = 20
# counter to track how many i've saved:
counter = 0
# master list that will be pickled / saved:
game_list = []
# I only want information on these units [zergling, marine, scv, drone, probe, zealot]:
valid_types = [37, 0, 7, 41, 64, 65]
# loop over replay master list, grab first "num_games_to_parse"
for full_filename in replays_master:
    if counter >= num_games_to_parse:
        break
    counter += 1

    replay = replayer.load(full_filename)
    print("loaded replay of length:" + str(len(replay)))
    all_frames = []
    for frame_number in range(len(replay)):
        frame = replay.getFrame(frame_number)
        units = frame.units
        this_frame = []
        for player_id, unit_arr in units.iteritems():
            if player_id < 0:
                # This is a map resource / object, not an army unit
                continue
            for unit in unit_arr:
                if unit.type in valid_types:
                    this_frame.append(unit_to_dict(unit))
        all_frames.append(this_frame)
    game_list.append(all_frames)

pickle_filename = str(num_games_to_parse)+"_games.pkl"
pickle.dump(game_list, open(pickle_filename, 'wb'))

