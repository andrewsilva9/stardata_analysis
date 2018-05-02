# Created by Andrew Silva on 4/19/18
# Yet another generate data file :(
# This heavily duplicates code from visualize_unit_movement. sorry :(
import torchcraft
from torchcraft import replayer
import os
import pickle
import numpy as np
import data_utils
from sklearn import cluster, mixture
from sklearn.neighbors import kneighbors_graph
from scipy import stats
from sklearn.externals import joblib
from pomegranate import *
import warnings
warnings.filterwarnings("ignore")

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


def unit_to_dict(unit_in,
                 unit_spawn,
                 all_units,
                 valid_types,
                 feature_set,
                 add_orders):
    """
    convert a unit to a dictionary of desired attributes. currently generating MIN dataset from feature_sets.md
    :param unit_in: unit to interpret
    :param unit_spawn: spawn point of unit (if -1, -1, consider this to be starting point)
    :param all_units: list of all units for this frame (necessary for neighbors)
    :param valid_types: list of valid unit types to consider (necessary for neighbors)
    :param feature_set: min, med, or max for feature set
    :param add_orders: include order info as feature
    :return: dictionary of {key: value} for all keys in unit_attrs global
    """
    min_feats = med_feats = max_feats = False
    if feature_set.lower() == 'max':
        min_feats = med_feats = max_feats = True
    elif feature_set.lower() == 'med':
        min_feats = med_feats = True
    elif feature_set.lower() == 'min':
        min_feats = True

    unit_dict = dict()

    if unit_spawn[0] < 0:
        unit_dict['distance_from_home'] = 0.0
    else:
        unit_dict['distance_from_home'] = distance_between(unit_spawn[0], unit_spawn[1], unit_in.x, unit_in.y) / 512.0
    unit_dict['x'] = unit_in.x
    unit_dict['y'] = unit_in.y
    if min_feats:
        unit_dict['percent_health'] = unit_in.health*1.0/unit_in.max_health
        nearby_allies = get_nearest_units(unit_in, all_units, valid_types)
        unit_dict['nearby_allies'] = nearby_allies*1.0/len(all_units)
    if med_feats:
        unit_dict['attacking'] = 1.0 if unit_in.attacking else 0.0
        unit_dict['mining'] = 1.0 if (unit_in.gathering_gas or unit_in.gathering_minerals or unit_in.carrying_gas or unit_in.carrying_minerals) else 0.0
        unit_dict['building'] = 1.0 if unit_in.constructing else 0.0
        unit_dict['visible'] = unit_in.visible
        unit_dict['size'] = unit_in.size
    if max_feats:
        unit_dict['type'] = unit_in.type
        unit_dict['armor'] = unit_in.armor
        if unit_in.maxCD > 0:
            unit_dict['current_cooldown'] = (unit_in.groundCD)*1.0/(unit_in.maxCD)
        else:
            unit_dict['current_cooldown'] = 0.0

    if add_orders:
        unit_dict['order'] = unit_in.orders[-1].type
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
                      threshold=10):
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


def game_over_time(replay,
                   valid_types,
                   playerid=0,
                   step_size=4,
                   feature_set='min',
                   add_orders=False):
    """
    turns a .tcr into an array of dictionaries for visualizing / processing
    :param replay: loaded replay data
    :param valid_types: list of unit_type attributes to consider
    :param playerid: player to follow (default 0)
    :param step_size: number of steps to skip between frames
    :param feature_set: min, med, or max set of features
    :param add_orders: include order details
    :return: array of dictionaries of unit data over time
    """
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
            for unit in unit_arr:
                if unit.type in valid_types:
                    if not unit.completed:
                        continue
                    if unit.id in starting_positions:
                        this_frame[unit.id] = unit_to_dict(unit,
                                                           starting_positions[unit.id],
                                                           unit_arr,
                                                           valid_types,
                                                           feature_set,
                                                           add_orders)
                    else:
                        this_frame[unit.id] = unit_to_dict(unit,
                                                           (-1, -1),
                                                           unit_arr,
                                                           valid_types,
                                                           feature_set,
                                                           add_orders)
                        starting_positions[unit.id] = (unit.x, unit.y)
        game_data.append(this_frame)
    return game_data


def post_process(game_array,
                n_timesteps=2):
    """
    takes in a game_over_time array and post-processes the data. For now that means optic flow / delta across frames
    WARNING: This returns a LOT of duplicate data. this is necessary for the drawing functionality (all of the frames
    of data need to be present so that every frame can be drawn). If you want to use this data for classification,
    you need to sample at n_timesteps from the data you get back from this function. Sorry.
    :param game_array: an array of a single game from game_over_time
    :param n_timesteps: size of window of observation
    :return game_array: an array of a single game where each unit gains features that are calculated across time"""
    final_game_data = []
    for frame_index in range(0, len(game_array), n_timesteps):
        upcoming_seq = game_array[frame_index]
        last_frame = frame_index+n_timesteps
        if last_frame >= len(game_array):
            last_frame = -1
#             continue  # Currently planning on only taking in n_timesteps, ignoring all else.
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
             n_timesteps=2,
             for_drawing=False):
    """
    takes in a game_over_time array and post-processes the data by linking up N consecutive timesteps into one array
    WARNING: See post_process warning. Sorry.
    :param game_array: an array of a single game from game_over_time
    :param n_timesteps: window of observation size
    :param for_drawing: if true, returns way too much data for sampling at draw time. set to false for hmm training data
    :return game_array: an array of a single game, where units are N timesteps longer
    """
    # TODO: Eventually, fix that this is seeing into the future
    final_game_data = []
    for frame_index in range(0, len(game_array), n_timesteps):

        to_add = {}
        upcoming_seq = {}
        starting_points = {}

        for frame_ind, frame in enumerate(game_array[frame_index:frame_index + n_timesteps]):

            for unit_id, unit_arr in frame.iteritems():
                if unit_id in upcoming_seq:
                    x_diff = starting_points[unit_id][0] - unit_arr['x']
                    y_diff = starting_points[unit_id][1] - unit_arr['y']
                    new_data = [x_diff, y_diff]
                else:
                    new_data = [0, 0]
                    starting_points[unit_id] = [unit_arr['x'], unit_arr['y']]
                    if frame_ind > frame_index:
                        # the 2 + is for x and y diff
                        filler_data = [[-1] * (2 + len(unit_arr))] * (frame_ind - frame_index)
                        upcoming_seq[unit_id] = filler_data
                    else:
                        upcoming_seq[unit_id] = []
                del unit_arr['x']
                del unit_arr['y']
                new_data.extend(unit_arr.values())
                upcoming_seq[unit_id].append(new_data)

        # Pad missing timesteps with -1s
        if upcoming_seq:
            filler_arr = [[-1] * len(new_data)]
            correct_length = n_timesteps
            for unit_id, unit_seq in upcoming_seq.iteritems():
                if len(unit_seq) < correct_length:
                    unit_seq += filler_arr * (correct_length - len(unit_seq))
                if for_drawing:
                    to_add[unit_id] = unit_seq
                else:
                    final_game_data.append(unit_seq)
            if for_drawing:
                for i in range(n_timesteps):
                    final_game_data.append(to_add)
    return final_game_data


def game_data_for_drawing(
        replay,
        valid_types,
        playerid=0,
        step_size=4):
        """
        turns a .tcr into an array of dictionaries for visualizing / processing
        :param replay: loaded replay data
        :param valid_types: list of unit_type attributes to consider
        :param playerid: player to follow (default 0)
        :param step_size: number of frames to skip between recordings
        :return: array of dictionaries of unit data over time
        """
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
               show_text=False,
               hmm_ind=None):
    """
    Takes in a dictionary unit and an image, and draws the units onto the image
    :param unit_dictionary_for_drawing: units to draw onto the image. dict should be {id: unit_to_dict_for_drawing, ...}
    :param unit_dictionary_for_classification: unit dictionary for classification. should be same format as above
    :param clf: classifier to use
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
            # FOR POMEGRANATE:
            # class_pred = clf.predict(np.array(unit_dictionary_for_classification[unit_id], dtype=np.float32),
            #                          algorithm="viterbi")[hmm_ind]
            # FOR HMMLEARN:
            class_pred = clf.predict(unit_dictionary_for_classification[unit_id])[hmm_ind]
            # class_pred = stats.mode(clf.predict(unit_dictionary_for_classification[unit_id]))[0][0]
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
                       window_size,
                       framerate=1,
                       save_video=False,
                       play_video=True,
                       show_text=False):
    """
    This will convert a .tcr into a crude visualized replay, squares for player 1, circles from player 0
    Default behavior will be to only follow player 0
    Default behavior will have units flash red if they are attacking
    Default behavior will scale unit size based on their percent health
    :param draw_data: unit dictionary with information necessary to draw units (see unit_to_dict_for_drawing)
    :param processed_data: unit dictionary with information for classifying units (see unit_to_dict)
    :param clf_name: for saving the video
    :param clf: classifer to classify units with
    :param window_size: how often to reset hmm_ind to 0
    :param framerate: how many frames to show each second for play_video
    :param save_video: True for saving output.avi, a copy of the video. False to not waste time saving a video
    :param play_video: True to display the video as it's being created. False to not waste time watching it be made
    :param show_text: draw unit names over their icons
    :return: True on success I guess?
    """
    # Define some params for the visualization:
    map_shape = (1024, 1024, 3)
    vid_name = clf_name + '.avi'
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(vid_name, fourcc, 20.0, (1024, 1024))
    wait_time = int(1000.0/framerate)
    hmm_ind = 0
    for frame_dict, pred_dict in zip(draw_data, processed_data):
        if hmm_ind >= window_size:
            hmm_ind = 0
        white_bg = np.ones(map_shape) * 255
        white_bg = draw_units(frame_dict, pred_dict, clf, white_bg, show_text=show_text, hmm_ind=hmm_ind)
        hmm_ind += 1
        if play_video:
            cv2.imshow('frame', white_bg)
            cv2.waitKey(wait_time)
        if save_video:
            out.write(np.uint8(white_bg))

    out.release()
    cv2.destroyAllWindows()
    return True


def hyper_params():
    param_dict = dict()
    # This file is generated from `get_good_replays.py`
    replays_master = open('good_files.txt', 'r').readlines()
    for i in range(len(replays_master)):
        replays_master[i] = replays_master[i].split('\n')[0]
    param_dict['replays_master'] = replays_master
    # this is how many games i'm going to save:
    param_dict['num_games_to_parse'] = 50
    # I only want information on these units:
    param_dict['terran_valid_types'] = [0, 1, 2, 3, 5, 7, 8, 9, 11, 12, 13, 30, 32, 34, 58]
    param_dict['zerg_valid_types'] = [37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 50, 62, 103]
    param_dict['protoss_valid_types'] = [60, 61, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 83, 84, 85]
    param_dict['zerg_babies'] = [35, 36, 59, 97]
    param_dict['valid_units'] = param_dict['terran_valid_types']  # + param_dict['zerg_valid_types'] + param_dict['protoss_valid_types']

    param_dict['replay_path'] = '/media/asilva/HD_home/StarData/dumped_replays/0/bwrep_poa7y.tcr'
    # param_dict['replay_path'] = '/media/asilva/HD_home/StarData/dumped_replays/1/bwrep_v8os7.tcr'

    param_dict['components'] = 10

    param_dict['step_frames'] = 4
    param_dict['window_size'] = 23
    param_dict['playerid'] = 2

    param_dict['feature_set'] = 'min'
    param_dict['add_orders'] = False

    return param_dict


if __name__ == '__main__':
    import cv2
    # replay_path = '/media/asilva/HD_home/StarData/dumped_replays/1/bwrep_v8os7.tcr'
    # all_games = []
    # for replay_path in replays_master:
    #     if len(all_games) >= num_games_to_parse:
    #         break
    #     game_info = game_over_time(replay_path, valid_types=valid_units, playerid=2, step_size=4)
    #     if game_info != -1:
    #         all_games.append(game_info)
    color_dict = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (100, 100, 100), (100, 100, 255),
                  (100, 255, 255), (10, 151, 226), (0, 255, 255), (0, 0, 255), (255, 100, 255), (0, 0, 0),
                  (160, 0, 255), (120, 0, 180), (0, 0, 100)]
    fps = 20

    params = hyper_params()

    save_vid = True
    play_vid = False
    draw_text = False
    # Load in the replay:
    replay = replayer.load(params['replay_path'])
    print("loaded replay: " + params['replay_path'] + " of length:" + str(len(replay)))

    game_data = game_data_for_drawing(replay=replay,
                                      valid_types=params['valid_units'],
                                      playerid=params['playerid'],
                                      step_size=params['step_frames'])
    print("draw data extracted")
    game_info = game_over_time(replay=replay,
                               valid_types=params['valid_units'],
                               playerid=params['playerid'],
                               step_size=params['step_frames'],
                               feature_set=params['feature_set'],
                               add_orders=params['add_orders'])
    print("raw data extracted")
    hmm_samples = hmm_data(game_info,
                           n_timesteps=params['window_size'],
                           for_drawing=True)
    print("hmm data post processed")

    # cls = joblib.load('clf/pomegranate5.pkl')
    # cls_name = params['replay_path'].split('/')[-1] + 'pom5'
    clf_name = 'clf/gaussianhmm' + str(params['components']) + params['feature_set'] + '.pkl'
    cls = joblib.load(clf_name)
    cls_name = params['replay_path'].split('/')[-1] + 'hmm' + str(params['components']) + params['feature_set']
    play_opencv_replay(draw_data=game_data,
                       processed_data=hmm_samples,
                       clf_name=cls_name,
                       clf=cls,
                       window_size=params['window_size'],
                       framerate=fps,
                       save_video=save_vid,
                       play_video=play_vid,
                       show_text=draw_text)

    # processed = post_process(game_info,
    #                          n_timesteps=window_size)
    #
    # X = []
    # for i in range(0, len(processed), window_size):
    #     X.extend(processed[i].values())
    #
    # num_clusters = 5
    # two_means = cluster.MiniBatchKMeans(n_clusters=num_clusters)
    # gmm = mixture.GaussianMixture(
    #     n_components=num_clusters,
    #     covariance_type='full')
    # clustering_algorithms = (
    #     ('MiniBatchKMeans', two_means),
    #     ('GaussianMixture', gmm)
    # )
    #
    # for name, cls in clustering_algorithms:
    #     cls.fit(X)
    #     joblib.dump(cls, 'clf/' + name + '.pkl')
    #     play_opencv_replay(game_data,
    #                        processed,
    #                        name,
    #                        cls,
    #                        framerate=fps,
    #                        save_video=save_vid,
    #                        play_video=play_vid,
    #                        show_text=draw_text)
