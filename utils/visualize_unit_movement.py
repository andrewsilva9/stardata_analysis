# Created by Andrew Silva on 4/18/18
# This file will open up an opencv frame with circles for units, one opencv frame per game frame. press 0 / whatever to
# step through frames of the game. Default will be 1fps
import torchcraft
from torchcraft import replayer
import os
import pickle
import numpy as np
import data_utils
import cv2

unit_attrs = ['type', 'x', 'y', 'size', 'pixel_x', 'pixel_y', 'pixel_size_x', 'pixel_size_y', 'playerId']
flags = ['accelerating', 'attacking', 'attack_frame', 'being_constructed', 'being_gathered', 'being_healed', 'blind', 'braking', 'burrowed', 'carrying_gas', 'carrying_minerals', 'cloaked', 'completed', 'constructing', 'defense_matrixed', 'detected', 'ensnared', 'flying', 'following', 'gathering_gas', 'gathering_minerals', 'hallucination', 'holding_position', 'idle', 'interruptible', 'invincible', 'irradiated', 'lifted', 'loaded', 'locked_down', 'maelstrommed', 'morphing', 'moving', 'parasited', 'patrolling', 'plagued', 'powered', 'repairing', 'researching', 'selected', 'sieged', 'starting_attack', 'stasised', 'stimmed', 'stuck', 'targetable', 'training', 'under_attack', 'under_dark_swarm', 'under_disruption_web', 'under_storm', 'upgrading']
# Uncomment for flags as attributes:
unit_attrs += flags


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

# This file is generated from `get_good_replays.py`
replays_master = open('good_files.txt', 'r').readlines()
for i in range(len(replays_master)):
    replays_master[i] = replays_master[i].split('\n')[0]


def play_opencv_replay(full_replay_path, playerid=0, framerate=1, save_video=False):
    """
    This will open the opencv frames, 1 per sec for stepping through a game
    Default behavior will be to only follow player 0
    Default behavior will also only consider workers and basic attackers.
    :param full_replay_path: full filename for replay (for example: '/media/asilva/StarCraft/bwrep_01234.tcr')
    :param playerid: id of player to show units for. 2 or greater for both players to be shown
    :return: True on success I guess?
    """
    # TODO: change color of unit or shape or whatever if they're attacking, losing health, order changing, whatever
    map_shape = (1024, 1024, 3)
    unit_scale = 4
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (1024, 1024))

    step_size = 8  # 1 frame per second if step size = 8
    replay = replayer.load(full_replay_path)
    wait_time = int(1000.0/framerate)
    print("loaded replay: " + full_replay_path + " of length:" + str(len(replay)))
    for frame_number in range(0, len(replay), step_size):
        frame = replay.getFrame(frame_number)
        units = frame.units
        this_frame = {}
        white_bg = np.ones(map_shape) * 255

        for player_id, unit_arr in units.iteritems():
            # I only want to look at the player i pass in (default 0)
            if player_id != playerid and playerid < 2:
                continue
            # For each unit in this frame:
            for unit in unit_arr:
                # Make sure it's a type that I care about
                if unit.type in valid_types:
                    # save it
                    this_frame[unit.id] = unit_to_dict(unit)
            # End iteration over units for player_id in this frame
        # End iteration over units for all players in this frame
        for unit_id, unit_dict in this_frame.iteritems():
            unit_color = color_dict[unit_dict['type']]
            if unit_dict['attacking']:
                unit_color = (0, 0, 255)
            if unit_dict['playerId'] == 0:
                unit_center = (unit_dict['x']*2, unit_dict['y']*2)
                cv2.circle(white_bg, unit_center,
                           unit_dict['size']*unit_scale,
                           color=unit_color,
                           thickness=-1)
            else:
                unit_top_left = (unit_dict['x'] * 2 - unit_dict['size'] * unit_scale,
                                 unit_dict['y'] * 2 - unit_dict['size'] * unit_scale)
                unit_bot_right = (unit_dict['x'] * 2 + unit_dict['size'] * unit_scale,
                                  unit_dict['y'] * 2 + unit_dict['size'] * unit_scale)
                cv2.rectangle(white_bg,
                              unit_top_left,
                              unit_bot_right,
                              color=unit_color,
                              thickness=-1)
        cv2.imshow('frame', white_bg)
        if save_video:
            out.write(np.uint8(white_bg))
        cv2.waitKey(wait_time)
    # End iteration over all frames
    out.release()
    cv2.destroyAllWindows()
    player0psi = frame.resources[0].used_psi
    player1psi = frame.resources[1].used_psi
    if player0psi > player1psi:
        print("I think player 0 won with " + str(player0psi-player1psi) + " more psi than player 1")
    else:
        print("I think player 1 won with " + str(player1psi-player0psi) + " more psi than player 1")

    return True


if __name__ == '__main__':

    # this is how many games i'm going to save:
    num_games_to_parse = 3
    # TODO: add more units to valid types and corresponding colors
    # I only want information on these units:
    terran_valid_types = [0, 1, 2, 3, 5, 7, 8, 9, 11, 12, 13, 30, 32, 33, 34, 58]
    zerg_valid_types = [37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 50, 62, 103]
    protoss_valid_types = [60, 61, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 83, 84, 85]
    zerg_babies = [35, 36, 59, 97]
    valid_types = terran_valid_types + zerg_valid_types + protoss_valid_types

    # map types to colors
    color_dict = {
        0: (0, 255, 0),
        1: (255, 85, 0),
        2: (70, 150, 0),
        3: (85, 85, 0),
        5: (100, 0, 200),
        30: (200, 200, 150),
        7: (255, 0, 0),
        8: (0, 255, 150),
        9: (0, 150, 255),
        11: (0, 85, 255),
        12: (255, 0, 255),
        13: (0, 0, 0),
        32: (15, 125, 150),
        33: (255, 0, 85),
        58: (85, 85, 85),
        34: (85, 0, 85),
        ################
        37: (0, 255, 0),
        38: (255, 85, 0),
        39: (70, 150, 0),
        40: (0, 0, 0),
        41: (255, 0, 0),
        42: (0, 255, 150),
        43: (0, 150, 255),
        44: (255, 0, 255),
        45: (255, 85, 255),
        46: (70, 150, 85),
        50: (0, 0, 0),
        62: (255, 255, 85),
        103: (85, 255, 255),
        ##################
        64: (255, 0, 0),
        65: (255, 85, 0),
        60: (70, 150, 0),
        61: (0, 0, 0),
        63: (0, 255, 0),
        66: (0, 255, 150),
        67: (0, 150, 255),
        68: (255, 0, 255),
        69: (255, 85, 255),
        70: (250, 150, 150),
        71: (0, 0, 0),
        72: (255, 255, 85),
        73: (85, 255, 255),
        83: (0, 85, 255),
        84: (255, 255, 0),
        85: (15, 125, 150)
                  }
    fps = 20
    replay_path = '/media/asilva/HD_home/StarData/dumped_replays/0/bwrep_poa7y.tcr'
    save_vid = True
    play_opencv_replay(replay_path, playerid=2, framerate=fps, save_video=save_vid)
