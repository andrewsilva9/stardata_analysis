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


# Currently not using flags (see above) or: Orders, Commands, crafted features (distance from start base, etc.)
def unit_to_dict(unit_in):
    unit_dict = {}
    unit_dict['type_name'] = type_to_name(unit.type)
    for attribute in unit_attrs:
        unit_dict[attribute] = getattr(unit, attribute)
    return unit_dict


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

# Look for any attack types that are not 1,2,3,5
master_unit_dict = {}
counter = 0
for full_filename in replays_master:
    counter += 1
    if counter >= 1001:
        break
    replay = replayer.load(full_filename)
    print("Loaded replay: " + str(full_filename) + " with length: " + str(len(replay)))
    # All units are in last frame so I only need that.
    last_frame = replay.getFrame(len(replay) - 1)
    units = last_frame.units
    for player_id, unit_arr in units.iteritems():
        if player_id < 0:
            # This is a map resource / object, not an army unit
            continue
        for unit in unit_arr:
            if unit.type in master_unit_dict:
                continue
            else:
                master_unit_dict[unit.type] = unit_to_dict(unit)

pickle.dump(master_unit_dict, open('sc_units.pkl', 'wb'))
