# Created by Andrew Silva on 4/19/18
# Yet another generate data file :(
# This heavily duplicates code from visualize_unit_movement. sorry :(
import torchcraft
from torchcraft import replayer
import os
import pickle
import numpy as np
import data_utils
from sklearn import cluster, datasets, mixture
from sklearn.neighbors import kneighbors_graph
from sklearn.externals import joblib

unit_attrs = ['type',
              'x',
              'y',
              'size',
              'playerId',
              'max_health',
              'health']
flags = ['accelerating', 'attacking', 'attack_frame', 'being_constructed', 'being_gathered', 'being_healed', 'blind', 'braking', 'burrowed', 'carrying_gas', 'carrying_minerals', 'cloaked', 'completed', 'constructing', 'defense_matrixed', 'detected', 'ensnared', 'flying', 'following', 'gathering_gas', 'gathering_minerals', 'hallucination', 'holding_position', 'idle', 'interruptible', 'invincible', 'irradiated', 'lifted', 'loaded', 'locked_down', 'maelstrommed', 'morphing', 'moving', 'parasited', 'patrolling', 'plagued', 'powered', 'repairing', 'researching', 'selected', 'sieged', 'starting_attack', 'stasised', 'stimmed', 'stuck', 'targetable', 'training', 'under_attack', 'under_dark_swarm', 'under_disruption_web', 'under_storm', 'upgrading']
# Uncomment for flags as attributes:
# unit_attrs += flags


def unit_to_dict(unit_in, unit_spawn, all_units, valid_types):
    """
    convert a unit to a dictionary of desired attributes. currently generating MIN dataset from feature_sets.md
    :param unit_in: unit to interpret
    :param unit_spawn: spawn point of unit (if -1, -1, consider this to be starting point)
    :param all_units: list of all units for this frame (necessary for neighbors)
    :param valid_types: list of valid unit types to consider (necessary for neighbors)
    :return: dictionary of {key: value} for all keys in unit_attrs global
    """
    MIN = True
    MED = False
    MAX = False
    unit_dict = dict()

    if unit_spawn[0] < 0:
        unit_dict['distance_from_home'] = 0.0
    else:
        unit_dict['distance_from_home'] = distance_between(unit_spawn[0], unit_spawn[1], unit_in.x, unit_in.y) / 512.0
    if MIN:
        unit_dict['percent_health'] = unit_in.health*1.0/unit_in.max_health
        nearby_allies = get_nearest_units(unit_in, all_units, valid_types)
        unit_dict['nearby_allies'] = nearby_allies*1.0/len(all_units)
    if MED:
        unit_dict['attacking'] = 1.0 if unit_in.attacking else 0.0
        unit_dict['mining'] = 1.0 if (unit_in.gathering_gas or unit_in.gathering_minerals or unit_in.carrying_gas or unit_in.carrying_minerals) else 0.0
        unit_dict['building'] = 1.0 if unit_in.constructing else 0.0
        unit_dict['visible'] = unit_in.visible
        unit_dict['size'] = unit_in.size
        # unit_dict['armor'] = unit_in.armor
    if MAX:
        # TODO: add MAX features
        unit_dict['type'] = unit_in.type
        # if unit_in.maxCD > 0:
        #     unit_dict['current_cooldown'] = (unit_in.groundCD)*1.0/(unit_in.maxCD)
        # else:
        #     unit_dict['current_cooldown'] = 0.0
    return unit_dict


def unit_to_dict_for_drawing(unit_in):
    """
    convert a unit to a dictionary of desired attributes. currently generating MIN dataset from feature_sets.md
    :param unit_in: unit to interpret
    :param unit_spawn: spawn point of unit (if -1, -1, consider this to be starting point)
    :param all_units: list of all units for this frame (necessary for neighbors)
    :param valid_types: list of valid unit types to consider (necessary for neighbors)
    :return: dictionary of {key: value} for all keys in unit_attrs global
    """
    unit_dict = dict()
    # Remove below for non-vis dataset
    for attribute in unit_attrs:
        unit_dict[attribute] = getattr(unit_in, attribute)
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
            if player_id != playerid and playerid < 2:
                continue
            elif player_id < 0:
                continue
            new_unit = False
            for unit in unit_arr:
                if unit.type in valid_types:
                    if not unit.completed:
                        continue
                    if unit.id in starting_positions:
                        this_frame[unit.id] = unit_to_dict(unit, starting_positions[unit.id], unit_arr, valid_types)
                    else:
                        new_unit = True
                        this_frame[unit.id] = unit_to_dict(unit, (-1, -1), unit_arr, valid_types)
                        starting_positions[unit.id] = (unit.x, unit.y)
            # TODO: this is the TvT hack. remove later?
            # if not new_unit and frame_number == 0:
            #     return -1
        game_data.append(this_frame)
    return game_data


def post_process(game_array,
                n_timesteps=2):
    """
    takes in a game_over_time array and post-processes the data. For now that means optic flow / delta across frames
    :param game_array: an array of a single game from game_over_time
    :return game_array: an array of a single game where each unit gains features that are calculated across time"""
    final_game_data = []
    for frame_index in range(0, len(game_array), n_timesteps):
        upcoming_seq = game_array[frame_index]
        last_frame = frame_index+n_timesteps
        if last_frame >= len(game_array):
            # last_frame = -1
            continue  # Currently planning on only taking in n_timesteps, ignoring all else.
        to_add = {}
        for unit_id in upcoming_seq.keys():
            # Commented out because I am currently not manufacturing new features
            # Calculate delta between last_frame and current frame:
            if unit_id in game_array[last_frame].keys():
                upcoming_seq[unit_id]['distance_moved'] = game_array[last_frame][unit_id]['distance_from_home'] - upcoming_seq[unit_id]['distance_from_home']
                upcoming_seq[unit_id]['health_change'] = game_array[last_frame][unit_id]['percent_health'] - upcoming_seq[unit_id]['percent_health']
            else:
                upcoming_seq[unit_id]['distance_moved'] = 0.0
                upcoming_seq[unit_id]['health_change'] = -1.0
            to_add[unit_id] = upcoming_seq[unit_id].values()
        for i in range(n_timesteps):
            final_game_data.append(to_add)
    return final_game_data


def hmm_data(game_array,
             n_timesteps=2):
    """
    takes in a game_over_time array and post-processes the data by linking up N consecutive timesteps into one array
    :param game_array: an array of a single game from game_over_time
    :return game_array: an array of a single game, where units are N timesteps longer
    """
    final_game_data = []
    for frame_index in range(0, len(game_array), n_timesteps):
        upcoming_seq = {}
        for frame in game_array[frame_index:frame_index+n_timesteps]:
            for unit_id, unit_arr in frame.iteritems():
                if unit_id in upcoming_seq:
                    upcoming_seq[unit_id].extend(unit_arr.values())
                else:
                    upcoming_seq[unit_id] = unit_arr.values()
        # Pad missing timesteps with -1s
        filler_arr = [-1]
        correct_length = len(unit_arr) * n_timesteps
        for unit_id, unit_seq in upcoming_seq.iteritems():
            if len(unit_seq) < correct_length:
                unit_seq += filler_arr * (correct_length - len(unit_seq))
            final_game_data.append(unit_seq)
    return final_game_data


def game_data_for_drawing(
        full_replay_path,
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

        for frame_number in range(0, len(replay), step_size):
            frame = replay.getFrame(frame_number)
            units = frame.units
            this_frame = {}

            for player_id, unit_arr in units.iteritems():
                if player_id != playerid and playerid < 2:
                    continue
                elif player_id < 0:
                    continue
                for unit in unit_arr:
                    if unit.type in valid_types:
                        if not unit.completed:
                            continue
                        this_frame[unit.id] = unit_to_dict_for_drawing(unit)
            game_data.append(this_frame)
        return game_data


def draw_units(unit_dictionary_for_drawing,
               unit_dictionary_for_classification,
               clf,
               image_in,
               show_text=False):
    """
    Takes in a dictionary unit and an image, and draws the units onto the image
    :param unit_dictionary: units to draw onto the image. dict should be {id: unit_to_dict, id2: unit_to_dict2, etc}
    :param image_in: image to draw onto
    :param show_text: print unit names over their icons
    :return: image after being drawn on
    """
    for unit_id, unit_dict in unit_dictionary_for_drawing.iteritems():
        if unit_dict['max_health'] <= 0:
            continue
        unit_scale = int(5 * (unit_dict['health'] * 1.0 / unit_dict['max_health']))
        if unit_id not in unit_dictionary_for_classification:
            unit_color = (255, 255, 255)
        else:
            class_pred = clf.predict(np.array(unit_dictionary_for_classification[unit_id]).reshape((1, -1)))[0]
            unit_color = color_dict[class_pred]
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
            unit_text = data_utils.type_to_name(unit_dict['type'])
            cv2.putText(image_in,
                        unit_text,
                        (unit_dict['x'] * 2 - len(unit_text) * 5, unit_dict['y'] * 2 - unit_scale),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 0))
    return image_in



def play_opencv_replay(draw_data,
                       processed_data,
                       clf_name,
                       clf,
                       framerate=1,
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
    vid_name = replay_path.split('/')[-1] + clf_name + '.avi'
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(vid_name, fourcc, 20.0, (1024, 1024))
    wait_time = int(1000.0/framerate)

    for frame_dict, pred_dict in zip(draw_data, processed_data):
        white_bg = np.ones(map_shape) * 255
        white_bg = draw_units(frame_dict, pred_dict, clf, white_bg, show_text=show_text)
        if play_video:
            cv2.imshow('frame', white_bg)
            cv2.waitKey(wait_time)
        if save_video:
            out.write(np.uint8(white_bg))

    out.release()
    cv2.destroyAllWindows()
    return True


if __name__ == '__main__':
    import cv2

    # This file is generated from `get_good_replays.py`
    replays_master = open('good_files.txt', 'r').readlines()
    for i in range(len(replays_master)):
        replays_master[i] = replays_master[i].split('\n')[0]

    # this is how many games i'm going to save:
    num_games_to_parse = 3
    # I only want information on these units:
    terran_valid_types = [0, 1, 2, 3, 5, 7, 8, 9, 11, 12, 13, 30, 32, 34, 58]
    zerg_valid_types = [37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 50, 62, 103]
    protoss_valid_types = [60, 61, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 83, 84, 85]
    zerg_babies = [35, 36, 59, 97]
    valid_units = terran_valid_types  # + zerg_valid_types + protoss_valid_types

    # replay_path = '/media/asilva/HD_home/StarData/dumped_replays/1/bwrep_lpkn5.tcr'
    replay_path = '/media/asilva/HD_home/StarData/dumped_replays/1/bwrep_zkcw9.tcr'
    # all_games = []
    # for replay_path in replays_master:
    #     if len(all_games) >= num_games_to_parse:
    #         break
    #     game_info = game_over_time(replay_path, valid_types=valid_units, playerid=2, step_size=4)
    #     if game_info != -1:
    #         all_games.append(game_info)

    color_dict = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (100, 100, 100), (100, 255, 100),
                  (100, 255, 255), (0, 255, 100), (0, 255, 255), (0, 0, 255), (0, 100, 255), (0, 0, 0),
                  (100, 0, 255), (255, 0, 100), (100, 0, 100)]
    step_frames = 4
    window_size = 8
    playerid = 2
    fps = 20
    save_vid = True
    play_vid = False
    draw_text = False
    # Load in the replay:
    game_data = game_data_for_drawing(replay_path,
                                      valid_units,
                                      playerid=playerid,
                                      step_size=step_frames)
    game_info = game_over_time(replay_path,
                               valid_types=valid_units,
                               playerid=playerid,
                               step_size=step_frames)

    processed = post_process(game_info,
                             n_timesteps=window_size)

    X = []
    for i in range(0, len(processed), window_size):
        X.extend(processed[i].values())

    num_clusters = 5
    two_means = cluster.MiniBatchKMeans(n_clusters=num_clusters)
    gmm = mixture.GaussianMixture(
        n_components=num_clusters,
        covariance_type='full')
    clustering_algorithms = (
        ('MiniBatchKMeans', two_means),
        ('GaussianMixture', gmm)
    )

    for name, clf in clustering_algorithms:
        clf.fit(X)
        joblib.dump(clf, 'clf/' + name + '.pkl')
        play_opencv_replay(game_data,
                           processed,
                           name,
                           clf,
                           framerate=fps,
                           save_video=save_vid,
                           play_video=play_vid,
                           show_text=draw_text)
