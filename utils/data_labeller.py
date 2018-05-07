# Created by Andrew Silva on 5/2/18

# (1) Select a set of games
# (2) Identify the list of roles within those games
# (3) Construct heuristics for labels
# (4) Visualize games with heuristics in place (text necessary too)
# (5) Build system to re-label those missed by heuristics
from torchcraft import replayer
import generate_role_datasets
import numpy as np
import data_utils
import cv2

params = generate_role_datasets.hyper_params()

color_dict = {
    -1: (0, 0, 255),
    0: (0, 255, 0),
    1: (255, 0, 0),
    2: (0, 255, 0),
    3: (0, 255, 0),
    4: (110, 255, 110),
    5: (10, 85, 150),
    6: (85, 85, 85),
    8: (0, 255, 0),
    9: (0, 255, 0),
    11: (0, 255, 0),
    12: (0, 255, 0),
    13: (0, 255, 0),
    32: (0, 255, 0),
    33: (0, 255, 0),
    58: (0, 255, 0),
    34: (0, 255, 0),
    ################
    37: (255, 0, 0),
    38: (255, 0, 0),
    39: (255, 0, 0),
    40: (255, 0, 0),
    41: (255, 0, 0),
    42: (255, 0, 0),
    43: (255, 0, 0),
    44: (255, 0, 0),
    45: (255, 0, 0),
    46: (255, 0, 0),
    50: (255, 0, 0),
    62: (255, 0, 0),
    103: (255, 0, 0),
    ##################
    64: (0, 0, 255),
    65: (0, 0, 255),
    60: (0, 0, 255),
    61: (0, 0, 255),
    63: (0, 0, 255),
    66: (0, 0, 255),
    67: (0, 0, 255),
    68: (0, 0, 255),
    69: (0, 0, 255),
    70: (0, 0, 255),
    71: (0, 0, 255),
    72: (0, 0, 255),
    73: (0, 0, 255),
    83: (0, 0, 255),
    84: (0, 0, 255),
    85: (110, 255, 255)
}

test_set_replays = params['replays_master'][-2:]

# If constantly carrying minerals / doing the mining set of actions, you're a miner
# If doing the building / constructing set of actions, you're a builder
# If moving away from home with no friends, you're a scout
# If moving away from home with some friends, you might be an escorter (repairing siege tanks)?
# If moving away from home with lots of friends, you are probably an attacker? unless you're expansion miners...
# If moving with attackers or escorts and a healer, support role?
# If moving towards home and you are an attacker, probably a defender
# If moving towards ally taking damage and you are an attacker, probably a defender
# If attacking in home base, a defender
# If patrolling, a patrol (how to get that?)
# If running home and damaged / taking damage, retreating? which is...defender?
# Other?

role_dict = {
    'miner': 0,
    'builder': 1,
    'scout': 2,
    'escort': 3,
    'attacker': 4,
    'support': 5,
    'defender': 6,
    'patrol': 7,
    'other': -1
}
reverse_role_dict = dict()
for key, val in role_dict.iteritems():
    reverse_role_dict[val] = key


def am_i_mining(potential_miner):
    mining_orders = [79,80,81,82,83,84,85,86,87,88,89,90]
    if potential_miner.gathering_gas or \
            potential_miner.gathering_minerals or \
            potential_miner.carrying_gas or \
            potential_miner.carrying_minerals or \
            potential_miner.orders[-1].type in mining_orders :
        return True
    else:
        return False


def am_i_building(potential_builder):
    building_orders = [30, 32, 33, 42, 43]
    if potential_builder.constructing or potential_builder.morphing or potential_builder.orders[-1].type in building_orders:
        return True
    else:
        return False


def am_i_attacking(potential_attacker,
                   target_from_home,
                   dist_from_home,
                   nearest_enemy_base,
                   target_from_enemy):
    attacking_orders = [8, 9, 10, 11, 12, 14, 64, 65]
    if nearest_enemy_base < dist_from_home or target_from_enemy < target_from_home:
        # Closer to opponent than to my base
        if potential_attacker.attacking or potential_attacker.orders[-1].type in attacking_orders:
            return True
    return False


def am_i_defending(potential_defender,
                   target_from_home,
                   dist_from_home,
                   dist_from_enemy,
                   target_from_enemy):
    attacking_orders = [8, 9, 10, 11, 12, 14, 64, 65]
    if dist_from_home < dist_from_enemy or target_from_home < target_from_enemy:
        # Closer to home than to enemy
        if potential_defender.attacking or potential_defender.orders[-1].type in attacking_orders:
            return True
    return False


def dist(unit, base):
    return np.sqrt((unit[0] - base[0])**2 + (unit[0] - base[1])**2)


def dist_to_nearest_base(unit_position, bases):
    nearest_base = 65000
    for base in bases:
        dist_to_base = dist(unit_position, base)
        if dist_to_base < nearest_base:
            nearest_base = dist_to_base
    return nearest_base


def get_unit_role(unit_in,
                  all_units,
                  player_bases,
                  last_location):
    """
    get role data from heuristics here
    :param unit_in: unit i want a role for
    :param all_units: all my allies
    :param player_bases: where is the rebel base?! seriously though. dict of lists of tuples of all base data
    :param last_location: where was I last?
    :return: int: unit role
    """
    if am_i_mining(unit_in):
        return role_dict['miner']
    if am_i_building(unit_in):
        return role_dict['builder']
    unit_pos = [unit_in.x, unit_in.y, unit_in.id]
    bases = player_bases[unit_in.playerId]
    enemy_bases = player_bases[((unit_in.playerId+1) % 2)]
    closest_base = dist_to_nearest_base(unit_pos, bases)

    # if last_location != unit_pos:
    #     last_nearest = dist_to_nearest_base(last_location, bases)
    # else:
    #     last_nearest = closest_base

    last_order = unit_in.orders[-1]
    last_order_target = [last_order.targetX, last_order.targetY]
    target_nearest_base = dist_to_nearest_base(last_order_target, bases)
    nearest_enemy = dist_to_nearest_base(unit_pos, enemy_bases)
    target_nearest_enemy = dist_to_nearest_base(last_order_target, enemy_bases)

    nearby_allies = get_nearest_units(unit_pos, all_units)

    target_in = [last_order.targetX, last_order.targetY, unit_in.id]
    allies_near_target = get_nearest_units(target_in, all_units)

    if am_i_attacking(unit_in,
                      target_from_home=target_nearest_base,
                      dist_from_home=closest_base,
                      nearest_enemy_base=nearest_enemy,
                      target_from_enemy=target_nearest_enemy):
        return role_dict['attacker']
    elif target_nearest_base > closest_base and allies_near_target > 1:
        return role_dict['attacker']
    elif am_i_defending(unit_in,
                        target_from_home=target_nearest_base,
                        dist_from_home=closest_base,
                        dist_from_enemy=nearest_enemy,
                        target_from_enemy=target_nearest_enemy):
        return role_dict['defender']

    elif target_nearest_base > closest_base and nearby_allies < 1:
        return role_dict['scout']

    return -1


def get_nearest_units(unit_in_pos,
                      all_units,
                      threshold=10):
    """
    return a count of nearby neighbors. buildings included.
    :param unit_in: unit to compare to as [x, y, id] tuple
    :param all_units: all units owned by the same player
    :param threshold: must be at least this close
    :return: number of nearby allies
    """
    nearby_allies = 0
    for unit in all_units:
        if unit.id == unit_in_pos[2]:
            continue

        unit_to_consider = [unit.x, unit.y]

        diff = dist([unit_in_pos[0], unit_in_pos[1]], unit_to_consider)
        if diff > threshold:
            continue
        else:
            nearby_allies += 1
    return nearby_allies


def game_role_data(replay_data,
                   valid_types,
                   playerid=2,
                   step_size=1):
    """
    turns a .tcr into an array of dictionaries for visualizing / processing
    :param replay_data: loaded replay data
    :param valid_types: list of unit_type attributes to consider
    :param playerid: player to follow (default 2 (both))
    :param step_size: number of steps to skip between frames
    :return: array of dictionaries of unit data over time
    """
    all_role_data = []

    main_base_ids = [106, 131, 154]
    last_frame = {}
    for frame_number in range(0, len(replay_data), step_size):
        frame = replay_data.getFrame(frame_number)
        units = frame.units
        this_frame = {}
        playerbases = {0: [], 1: []}

        # Get the base locations
        for p_id, base_hunter in units.iteritems():
                for maybe_base in base_hunter:
                    if maybe_base.type in main_base_ids:
                        playerbases[p_id].append([maybe_base.x, maybe_base.y])
        # Get the real data
        for player_id, unit_arr in units.iteritems():
            if player_id != playerid and playerid < 2:
                continue
            elif player_id < 0:
                continue
            for unit in unit_arr:
                #TODO valid_types should be... all mobile units? all units including buildings?
                if unit.type in valid_types:
                    if not unit.completed:
                        continue
                    if unit.id in last_frame.keys():
                        last_position = last_frame[unit.id]
                    else:
                        last_position = [unit.x, unit.y]
                    this_frame[unit.id] = get_unit_role(unit,
                                                        unit_arr,
                                                        playerbases,
                                                        last_position)
                    last_frame[unit.id] = [unit.x, unit.y]
        all_role_data.append(this_frame)
    return all_role_data


def draw_units(unit_dictionary_for_drawing,
               unit_dictionary_for_coloring,
               image_in,
               show_text=False):
    """
    Takes in a dictionary unit and an image, and draws the units onto the image
    :param unit_dictionary_for_drawing: units to draw onto the image. dict should be {id: unit_to_dict_for_drawing, ...}
    :param unit_dictionary_for_coloring: unit dictionary for coloring. should be same format as above
    :param clf: classifier to use
    :param image_in: image to draw onto
    :param show_text: print unit names over their icons
    :return: image after being drawn on
    """
    for unit_id, unit_dict in unit_dictionary_for_drawing.iteritems():
        if unit_dict['max_health'] <= 0:
            continue
        unit_scale = int(5 * (unit_dict['health'] * 1.0 / unit_dict['max_health']))
        if unit_id not in unit_dictionary_for_coloring:
            unit_color = (0, 0, 0)
        else:
            unit_color = color_dict[unit_dictionary_for_coloring[unit_id]]
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
            unit_text = data_utils.type_to_name(unit_dict['type']).split('_')[-1]
            if unit_id in unit_dictionary_for_coloring:
                unit_text = unit_text + '_' + reverse_role_dict[unit_dictionary_for_coloring[unit_id]]
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
    for frame_dict, pred_dict in zip(draw_data, processed_data):
        white_bg = np.ones(map_shape) * 255
        white_bg = draw_units(frame_dict, pred_dict, white_bg, show_text=show_text)
        if play_video:
            cv2.imshow('frame', white_bg)
            cv2.waitKey(wait_time)
        if save_video:
            out.write(np.uint8(white_bg))

    out.release()
    cv2.destroyAllWindows()
    return True

if __name__ == "__main__":
    print test_set_replays
    for replay_path in test_set_replays:
        replay = replayer.load(replay_path)
        print("loaded replay: " + replay_path + " of length:" + str(len(replay)))
        valid_draw_units = np.arange(0, 203).tolist()
        valid_role_units = params['terran_valid_types'] + params['zerg_valid_types'] + params['protoss_valid_types']
        draw_data = generate_role_datasets.game_data_for_drawing(replay=replay,
                                                                 valid_types=valid_draw_units,
                                                                 playerid=2,
                                                                 step_size=1)
        print("Draw data loaded")
        role_data = game_role_data(replay_data=replay,
                                   valid_types=valid_role_units,
                                   playerid=2,
                                   step_size=1)
        print("Roles assigned")
        movie_name = replay_path.split('/')[-1] + 'GT'

        save_vid = True
        play_vid = False
        draw_text = True
        fps = 8
        play_opencv_replay(draw_data=draw_data,
                           processed_data=role_data,
                           clf_name=movie_name,
                           framerate=fps,
                           save_video=save_vid,
                           play_video=play_vid,
                           show_text=draw_text)
