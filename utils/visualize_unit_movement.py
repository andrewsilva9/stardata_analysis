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

unit_attrs = ['type',
              'x',
              'y',
              'size',
              'playerId',
              'max_health',
              'health']
flags = ['accelerating', 'attacking', 'attack_frame', 'being_constructed', 'being_gathered', 'being_healed', 'blind', 'braking', 'burrowed', 'carrying_gas', 'carrying_minerals', 'cloaked', 'completed', 'constructing', 'defense_matrixed', 'detected', 'ensnared', 'flying', 'following', 'gathering_gas', 'gathering_minerals', 'hallucination', 'holding_position', 'idle', 'interruptible', 'invincible', 'irradiated', 'lifted', 'loaded', 'locked_down', 'maelstrommed', 'morphing', 'moving', 'parasited', 'patrolling', 'plagued', 'powered', 'repairing', 'researching', 'selected', 'sieged', 'starting_attack', 'stasised', 'stimmed', 'stuck', 'targetable', 'training', 'under_attack', 'under_dark_swarm', 'under_disruption_web', 'under_storm', 'upgrading']
# Uncomment for flags as attributes:
unit_attrs += flags


def unit_to_dict(unit_in, unit_spawn, all_units, valid_types):
    """
    convert a unit to a dictionary of desired attributes
    :param unit_in: unit to interpret
    :param unit_spawn: spawn point of unit (if -1, -1, consider this to be starting point)
    :param all_units: list of all units for this frame (necessary for neighbors)
    :param valid_types: list of valid unit types to consider (necessary for neighbors)
    :return: dictionary of {key: value} for all keys in unit_attrs global
    """
    unit_dict = dict()
    # for attribute in unit_attrs:
    #     unit_dict[attribute] = getattr(unit_in, attribute)
    unit_dict['perc_health'] = unit_in.health*1.0/unit_in.max_health
    unit_dict['perc_ground_cd'] = unit_in.groundCD*1.0/unit_in.maxCD
    if unit_spawn[0] < 0:
        unit_dict['distance_from_home'] = 0.0
    else:
        unit_dict['distance_from_home'] = distance_between(unit_spawn[0], unit_spawn[1], unit_in.x, unit_in.y) / 724.07
    nearby_allies = get_nearest_units(unit_in, all_units, valid_types)
    unit_dict['nearby_allies'] = nearby_allies
    return unit_dict


def get_nearest_units(unit_in,
                      all_units,
                      valid_types,
                      threshold=20):
    """
    return a np array of self + nearest n_nearest units
    :param unit_in: unit to compare to
    :param all_units: all units owned by the same player
    :param valid_types: list of unit_type attributes that i want to consider
    :param threshold: must be at least this close
    :return: number of nearby allies
    """
    nearby_allies = 0
    for unit in all_units:
        if unit.id == unit_in.id:
            continue
        # If unit is not a valid unit
        if unit.type not in valid_types:
            continue
        diff = distance_between(unit.x, unit.y, unit_in.x, unit_in.y)
        if diff > threshold:
            continue
        else:
            # Don't need to compare playerId because unit_arr is always the same playerId as me
            nearby_allies += 1
    return nearby_allies


def distance_between(x1, y1, x2, y2):
    return np.sqrt((x1-x2)**2 + (y1-y2)**2)


def draw_units(unit_dictionary,
               image_in,
               show_text=False):
    """
    Takes in a dictionary unit and an image, and draws the units onto the image
    :param unit_dictionary: units to draw onto the image. dict should be {id: unit_to_dict, id2: unit_to_dict2, etc}
    :param image_in: image to draw onto
    :param show_text: print unit names over their icons
    :return: image after being drawn on
    """
    for unit_id, unit_dict in unit_dictionary.iteritems():
        if unit_dict['max_health'] <= 0:
            continue
        unit_scale = int(5 * (unit_dict['health'] * 1.0 / unit_dict['max_health']))

        unit_color = color_dict[unit_dict['type']]
        if unit_dict['attacking']:
            unit_color = (0, 0, 255)
        if unit_dict['playerId'] == 0:
            unit_center = (unit_dict['x'] * 2, unit_dict['y'] * 2)
            cv2.circle(image_in, unit_center,
                       unit_dict['size'] * unit_scale,
                       color=unit_color,
                       thickness=-1)
        else:
            unit_top_left = (unit_dict['x'] * 2 - unit_dict['size'] * unit_scale,
                             unit_dict['y'] * 2 - unit_dict['size'] * unit_scale)
            unit_bot_right = (unit_dict['x'] * 2 + unit_dict['size'] * unit_scale,
                              unit_dict['y'] * 2 + unit_dict['size'] * unit_scale)
            cv2.rectangle(image_in,
                          unit_top_left,
                          unit_bot_right,
                          color=unit_color,
                          thickness=-1)
        if show_text:
            unit_text = data_utils.type_to_name(unit_dict['type']) + "{:.2f}".format(unit_dict['distance_from_home'])
            cv2.putText(image_in,
                        unit_text,
                        (unit_dict['x'] * 2 - len(unit_text) * 5, unit_dict['y'] * 2 - unit_scale),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 0))
    return image_in


def game_over_time(full_replay_path,
                   valid_types,
                   playerid=0,
                   step_size=4):
    """
    turns a .tcr into an array of dictionaries for visualizing / processing
    :param full_replay_path: path to replay file
    :param valid_types: list of unit_type attributes to consider
    :param playerid: player to follow (default 0)
    :return: array of dictionaries of unit data over time
    """
    # Load in the replay:
    replay = replayer.load(full_replay_path)
    print("loaded replay: " + full_replay_path + " of length:" + str(len(replay)))
    game_data = []

    starting_positions = {}
    for frame_number in range(0, len(replay), step_size):
        frame = replay.getFrame(frame_number)
        units = frame.units
        this_frame = {}

        for player_id, unit_arr in units.iteritems():
            # I only want to look at the player i pass in (default 0)
            if player_id != playerid and playerid < 2:
                continue
            # For each unit in this frame:
            for unit in unit_arr:
                # Make sure it's a type that I care about
                if unit.type in valid_types:
                    if unit.id in starting_positions:
                        this_frame[unit.id] = unit_to_dict(unit, starting_positions[unit.id], unit_arr, valid_types)
                    else:
                        this_frame[unit.id] = unit_to_dict(unit, (-1, -1),  unit_arr, valid_types)
                        starting_positions[unit.id] = (unit.x, unit.y)
            # End iteration over units for player_id in this frame
        # End iteration over units for all players in this frame
        game_data.append(this_frame)
    # End iteration over all frames
    player0psi = frame.resources[0].used_psi
    player1psi = frame.resources[1].used_psi
    if player0psi > player1psi:
        print("I think player 0 won with " + str(player0psi - player1psi) + " more psi than player 1")
    else:
        print("I think player 1 won with " + str(player1psi - player0psi) + " more psi than player 0")
    return game_data


def play_opencv_replay(full_replay_path,
                       valid_types,
                       playerid=0,
                       framerate=1,
                       step_size=4,
                       save_video=False,
                       play_video=True,
                       show_text=False):
    """
    This will convert a .tcr into a crude visualized replay, squares for player 1, circles from player 0
    Default behavior will be to only follow player 0
    Default behavior will have units flash red if they are attacking
    Default behavior will scale unit size based on their percent health
    :param full_replay_path: full filename for replay (for example: '/media/asilva/StarCraft/bwrep_01234.tcr')
    :param valid_types: list of unit_types to consider
    :param playerid: id of player to show units for. 2 or greater for both players to be shown
    :param framerate: number of frames per second when playing video
    :param step_size: how many many steps forward through the replay should each frame be
    :param save_video: True for saving output.avi, a copy of the video. False to not waste time saving a video
    :param play_video: True to display the video as it's being created. False to not waste time watching it be made
    :param show_text: draw unit names over their icons
    :return: True on success I guess?
    """
    # Define some params for the visualization:
    map_shape = (1024, 1024, 3)
    vid_name = replay_path.split('/')[-1] + '.avi'
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(vid_name, fourcc, 20.0, (1024, 1024))
    wait_time = int(1000.0/framerate)

    # Load in the replay:
    game_data = game_over_time(full_replay_path,
                               valid_types,
                               playerid=playerid,
                               step_size=step_size)

    for frame_dict in game_data:
        white_bg = np.ones(map_shape) * 255
        white_bg = draw_units(frame_dict, white_bg, show_text=show_text)
        if play_video:
            cv2.imshow('frame', white_bg)
            cv2.waitKey(wait_time)
        if save_video:
            out.write(np.uint8(white_bg))

    out.release()
    cv2.destroyAllWindows()
    return True


if __name__ == '__main__':

    # This file is generated from `get_good_replays.py`
    replays_master = open('good_files.txt', 'r').readlines()
    for i in range(len(replays_master)):
        replays_master[i] = replays_master[i].split('\n')[0]

    # this is how many games i'm going to save:
    num_games_to_parse = 3
    # I only want information on these units:
    terran_valid_types = [0, 1, 2, 3, 5, 7, 8, 9, 11, 12, 13, 30, 32, 33, 34, 58]
    zerg_valid_types = [37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 50, 62, 103]
    protoss_valid_types = [60, 61, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 83, 84, 85]
    zerg_babies = [35, 36, 59, 97]
    valid_units = terran_valid_types + zerg_valid_types + protoss_valid_types

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
        65: (0, 255, 0),
        60: (70, 150, 0),
        61: (0, 0, 0),
        63: (85, 255, 0),
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
    fps = 1
    replay_path = '/media/asilva/HD_home/StarData/dumped_replays/0/bwrep_poa7y.tcr'
    step_frames = 500
    save_vid = False
    play_vid = True
    draw_text = True
    play_opencv_replay(replay_path,
                       valid_units,
                       playerid=2,
                       framerate=fps,
                       step_size=step_frames,
                       save_video=save_vid,
                       play_video=play_vid,
                       show_text=draw_text)
