import pickle
import numpy as np

bad_keys = ['x', 'y', 'velocityX', 'velocityY', 'resources', 'pixel_x', 'pixel_y', 'groundCD', 'airCD', 'health',
            'shield', 'playerId', 'energy', 'type_name', 'type']


def unit_pickle_to_xy(filename_in):
    raw_data = pickle.load(open(filename_in, 'rb'))
    X, Y = [], []
    for unit_id, unit in raw_data.iteritems():
        unit_attributes = []
        for attr_name, attribute in unit.iteritems():
            if attr_name in bad_keys:
                continue
            else:
                unit_attributes.append(attribute)
        X.append(unit_attributes)
        Y.append(unit_id)
    return X, Y


def game_pickle_to_xy(filename_in):
    raw_data = pickle.load(open(filename_in, 'rb'))
    X, Y = [], []
    for frame in raw_data:
        units = frame.units
        for unit in units:
            unit_attributes = []
            for attr_name, attribute in unit.iteritems():
                if attr_name in bad_keys:
                    continue
                else:
                    unit_attributes.append(attribute)
            X.append(unit_attributes)
            Y.append(unit_id)
    return X, Y



id2unit = [
    ("Terran_Marine", "0"),
    ("Terran_Ghost", "1"),
    ("Terran_Vulture", "2"),
    ("Terran_Goliath", "3"),
    ("Terran_Siege_Tank_Tank_Mode", "5"),
    ("Terran_SCV", "7"),
    ("Terran_Wraith", "8"),
    ("Terran_Science_Vessel", "9"),
    ("Terran_Dropship", "11"),
    ("Terran_Battlecruiser", "12"),
    ("Terran_Vulture_Spider_Mine", "13"),
    ("Terran_Nuclear_Missile", "14"),
    ("Terran_Civilian", "15"),
    ("Terran_Siege_Tank_Siege_Mode", "30"),
    ("Terran_Firebat", "32"),
    ("Spell_Scanner_Sweep", "33"),
    ("Terran_Medic", "34"),
    ("Zerg_Larva", "35"),
    ("Zerg_Egg", "36"),
    ("Zerg_Zergling", "37"),
    ("Zerg_Hydralisk", "38"),
    ("Zerg_Ultralisk", "39"),
    ("Zerg_Broodling", "40"),
    ("Zerg_Drone", "41"),
    ("Zerg_Overlord", "42"),
    ("Zerg_Mutalisk", "43"),
    ("Zerg_Guardian", "44"),
    ("Zerg_Queen", "45"),
    ("Zerg_Defiler", "46"),
    ("Zerg_Scourge", "47"),
    ("Zerg_Infested_Terran", "50"),
    ("Terran_Valkyrie", "58"),
    ("Zerg_Cocoon", "59"),
    ("Protoss_Corsair", "60"),
    ("Protoss_Dark_Templar", "61"),
    ("Zerg_Devourer", "62"),
    ("Protoss_Dark_Archon", "63"),
    ("Protoss_Probe", "64"),
    ("Protoss_Zealot", "65"),
    ("Protoss_Dragoon", "66"),
    ("Protoss_High_Templar", "67"),
    ("Protoss_Archon", "68"),
    ("Protoss_Shuttle", "69"),
    ("Protoss_Scout", "70"),
    ("Protoss_Arbiter", "71"),
    ("Protoss_Carrier", "72"),
    ("Protoss_Interceptor", "73"),
    ("Protoss_Reaver", "83"),
    ("Protoss_Observer", "84"),
    ("Protoss_Scarab", "85"),
    ("Critter_Rhynadon", "89"),
    ("Critter_Bengalaas", "90"),
    ("Critter_Scantid", "93"),
    ("Critter_Kakaru", "94"),
    ("Critter_Ragnasaur", "95"),
    ("Critter_Ursadon", "96"),
    ("Zerg_Lurker_Egg", "97"),
    ("Zerg_Lurker", "103"),
    ("Spell_Disruption_Web", "105"),
    ("Terran_Command_Center", "106"),
    ("Terran_Comsat_Station", "107"),
    ("Terran_Nuclear_Silo", "108"),
    ("Terran_Supply_Depot", "109"),
    ("Terran_Refinery", "110"),
    ("Terran_Barracks", "111"),
    ("Terran_Academy", "112"),
    ("Terran_Factory", "113"),
    ("Terran_Starport", "114"),
    ("Terran_Control_Tower", "115"),
    ("Terran_Science_Facility", "116"),
    ("Terran_Covert_Ops", "117"),
    ("Terran_Physics_Lab", "118"),
    ("Terran_Machine_Shop", "120"),
    ("Terran_Engineering_Bay", "122"),
    ("Terran_Armory", "123"),
    ("Terran_Missile_Turret", "124"),
    ("Terran_Bunker", "125"),
    ("Zerg_Infested_Command_Center", "130"),
    ("Zerg_Hatchery", "131"),
    ("Zerg_Lair", "132"),
    ("Zerg_Hive", "133"),
    ("Zerg_Nydus_Canal", "134"),
    ("Zerg_Hydralisk_Den", "135"),
    ("Zerg_Defiler_Mound", "136"),
    ("Zerg_Greater_Spire", "137"),
    ("Zerg_Queens_Nest", "138"),
    ("Zerg_Evolution_Chamber", "139"),
    ("Zerg_Ultralisk_Cavern", "140"),
    ("Zerg_Spire", "141"),
    ("Zerg_Spawning_Pool", "142"),
    ("Zerg_Creep_Colony", "143"),
    ("Zerg_Spore_Colony", "144"),
    ("Zerg_Sunken_Colony", "146"),
    ("Zerg_Extractor", "149"),
    ("Protoss_Nexus", "154"),
    ("Protoss_Robotics_Facility", "155"),
    ("Protoss_Pylon", "156"),
    ("Protoss_Assimilator", "157"),
    ("Protoss_Observatory", "159"),
    ("Protoss_Gateway", "160"),
    ("Protoss_Photon_Cannon", "162"),
    ("Protoss_Citadel_of_Adun", "163"),
    ("Protoss_Cybernetics_Core", "164"),
    ("Protoss_Templar_Archives", "165"),
    ("Protoss_Forge", "166"),
    ("Protoss_Stargate", "167"),
    ("Protoss_Fleet_Beacon", "169"),
    ("Protoss_Arbiter_Tribunal", "170"),
    ("Protoss_Robotics_Support_Bay", "171"),
    ("Protoss_Shield_Battery", "172"),
    ("Resource_Mineral_Field", "176"),
    ("Resource_Mineral_Field_Type_2", "177"),
    ("Resource_Mineral_Field_Type_3", "178"),
    ("Resource_Vespene_Geyser", "188"),
    ("Spell_Dark_Swarm", "202")
]

def type_to_name(type_in):
    # Limiting to the attacking units in id2unit. open it up later?
    for unit_tuple in id2unit:
        if int(unit_tuple[1]) == type_in:
            return unit_tuple[0]
    return "Not a valid attacking unit"
