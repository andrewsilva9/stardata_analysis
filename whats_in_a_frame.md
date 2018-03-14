# What's in a frame?
```
That which we call a frame
By any other word is a spreadsheet
```
[Well, I tried.](https://en.wikipedia.org/wiki/A_rose_by_any_other_name_would_smell_as_sweet) Anyway, so far here is what I have found.

## Inside a 'Replay':

### Map
Map is technically not in a frame, but in the replay file itself. `replay.getMap()` returns several 2D arrays, which include:

* `buildability` : presumably area that is valid for building or not. 1 for yes, 0 for no. Size is just map_size (512x512 for most?)
* `walkability` : squares which are valid to walk on or not. 1 for yes, 0 for now. Size is also map_size
* `ground_height` : height of each square. 0 for invalid, 1 for low, 2 for normal, 3 for high? Unsure.
* `start_locations` : a 4x2 of possible starting locations for each player. 4 possible locations, each with an (x,y)

### Other:

Other things inside a replay include: 
```
replay.getKeyFrame()
replay.getNumUnits()
```
Honestly, not sure what they do.

## Inside a 'Frame':

`replay.getFrame(int frame)` returns the frame with all game-state information for `int frame`. 

### frame.units

`frame.units` has probably the most important game state information in it. Everything is a unit: minerals, buildings, and actual units (probes, marines, whatnot). Units have a lot of information associated with them, including:

* `id` : unique identifier for each unit
* `x` : x coordinate
* `y` : y coordinate
* `health` : current health
* `max_health` : max health
* `shield` : current shield health / charge
* `max_shield` : max shield charge
* `energy` : energy? maybe like mana or magic or something?
* `maxCD` : Not sure. I really need to watch some starcraft
* `groundCD`: Not sure
* `airCD` : Not sure
* `visible`: Presumably 1 for yes, 0 for no (it is at least 1 for most units)
* `type`: int that ties to a list of unit classes (so 64 = "Protoss Probe", for example)
* `armor`: current armor?
* `shieldArmor` : another type of armor?
* `size`: I'm not sure of what this is. Internal size metric I suppose?
* `pixel_x`: Pixel position of unit? Rather than map coordinate
* `pixel_y`: Same as above
* `pixel_size_x`: Size of unit in pixels (x)
* `pixel_size_y`: Size of unit in pixels (y)
* `groundATK`: Unsure. Damage a unit does to ground units?
* `airATK`: Same as above (to air units)
* `groundDmgType`: Unsure. An enum for damage type?
* `airDmgType`: Same as above.
* `groundRange`: Unsure. Range of attack / interaction with ground units?
* `airRange`: Same as above (for air units)
* `velocityX`: Current velocity in x direction?
* `velocityY`: Current velocity in y direction?
* `playerId`: Player this unit belongs to (0, 1, or -1 for map resources)
* `resources`: Unsure

Units also have a bunch of flags that indicate what they are doing at any given moment, or otherwise what "state" they are in. I don't yet have any idea of what these flags mean, other than to guess by the names. They are:

* `accelerating`
* `attacking`
* `attack_frame`
* `being_constructed`
* `being_gathered`
* `being_healed`
* `blind`
* `braking`
* `burrowed`
* `carrying_gas`
* `carrying_minerals`
* `cloaked`
* `completed`
* `constructing`
* `defense_matrixed`
* `detected`
* `ensnared`
* `flying`
* `following`
* `gathering_gas`
* `gathering_minerals`
* `hallucination`
* `holding_position`
* `idle`
* `interruptible`
* `invincible`
* `irradiated`
* `lifted`
* `loaded`
* `locked_down`
* `maelstrommed`
* `morphing`
* `moving`
* `parasited`
* `patrolling`
* `plagued`
* `powered`
* `repairing`
* `researching`
* `selected`
* `sieged`
* `starting_attack`
* `stasised`
* `stimmed`
* `stuck`
* `targetable`
* `training`
* `under_attack`
* `under_dark_swarm`
* `under_disruption_web`
* `under_storm`
* `upgrading`

TODO with regard to units:
- [ ] figure out when they die (health doesn't drop to 0)
- [ ] learn more about the mapping between `size` and `pixel_size` / `x` and `pixel_x` and `velocity_x`, etc.
- [ ] learn what the flags mean
- [ ] learn what `CD` is, and what the `CD` and `ATK` numbers mean
- [ ] find a mapping for attack types? if this is useful?

### frame.resources

Probably second-most important for understanding a frame is the "resources" attribute. It is also much simpler to parse. For each player_id in the frame, there is a "resources" object. It contains:

* `player_id` : the player that these resources belong to
* `gas` : int, the amount of gas a player has
* `ore` : int, the amount of ore / minerals a player has
* `used_psi` : int, the psi a player has used? Not sure what this is. Supply maybe? Army size?
* `total_psi` : int, total available psi to a player. Again, supply? Army capacity?

TODO with regard to resources:
- [ ] learn what 'psi' is

### frame.bullets

I'm not entirely sure what "bullets" are, but they have only 3 attributes:

* `type` : int, probably an enum?
* `x` : probably a coordinate?
* `y` : probably a coordinate?

### Other:

Frames have other information in them, though it appears to be useless. The other accessible attributes are:
```
frame.actions
frame.reward
frame.is_terminal
```
I have confirmation from the author that "is_terminal" is just leftover from their work and is meaningless. "Actions" appears to be an empty dictionary in every frame, and "reward" seems to be 0 in every frame. So I'm not sure what these are for, but they don't appear immediately useful.

Finally, a useful list for unit types:
* "Terran_Marine" = 0
* "Terran_Ghost" = 1
* "Terran_Vulture" = 2
* "Terran_Goliath" = 3
* "Terran_Siege_Tank_Tank_Mode" = 5
* "Terran_SCV" = 7
* "Terran_Wraith" = 8
* "Terran_Science_Vessel" = 9
* "Terran_Dropship" = 11
* "Terran_Battlecruiser" = 12
* "Terran_Vulture_Spider_Mine" = 13
* "Terran_Nuclear_Missile" = 14
* "Terran_Civilian" = 15
* "Terran_Siege_Tank_Siege_Mode" = 30
* "Terran_Firebat" = 32
* "Spell_Scanner_Sweep" = 33
* "Terran_Medic" = 34
* "Zerg_Larva" = 35
* "Zerg_Egg" = 36
* "Zerg_Zergling" = 37
* "Zerg_Hydralisk" = 38
* "Zerg_Ultralisk" = 39
* "Zerg_Broodling" = 40
* "Zerg_Drone" = 41
* "Zerg_Overlord" = 42
* "Zerg_Mutalisk" = 43
* "Zerg_Guardian" = 44
* "Zerg_Queen" = 45
* "Zerg_Defiler" = 46
* "Zerg_Scourge" = 47
* "Zerg_Infested_Terran" = 50
* "Terran_Valkyrie" = 58
* "Zerg_Cocoon" = 59
* "Protoss_Corsair" = 60
* "Protoss_Dark_Templar" = 61
* "Zerg_Devourer" = 62
* "Protoss_Dark_Archon" = 63
* "Protoss_Probe" = 64
* "Protoss_Zealot" = 65
* "Protoss_Dragoon" = 66
* "Protoss_High_Templar" = 67
* "Protoss_Archon" = 68
* "Protoss_Shuttle" = 69
* "Protoss_Scout" = 70
* "Protoss_Arbiter" = 71
* "Protoss_Carrier" = 72
* "Protoss_Interceptor" = 73
* "Protoss_Reaver" = 83
* "Protoss_Observer" = 84
* "Protoss_Scarab" = 85
* "Critter_Rhynadon" = 89
* "Critter_Bengalaas" = 90
* "Critter_Scantid" = 93
* "Critter_Kakaru" = 94
* "Critter_Ragnasaur" = 95
* "Critter_Ursadon" = 96
* "Zerg_Lurker_Egg" = 97
* "Zerg_Lurker" = 103
* "Spell_Disruption_Web" = 105
* "Terran_Command_Center" = 106
* "Terran_Comsat_Station" = 107
* "Terran_Nuclear_Silo" = 108
* "Terran_Supply_Depot" = 109
* "Terran_Refinery" = 110
* "Terran_Barracks" = 111
* "Terran_Academy" = 112
* "Terran_Factory" = 113
* "Terran_Starport" = 114
* "Terran_Control_Tower" = 115
* "Terran_Science_Facility" = 116
* "Terran_Covert_Ops" = 117
* "Terran_Physics_Lab" = 118
* "Terran_Machine_Shop" = 120
* "Terran_Engineering_Bay" = 122
* "Terran_Armory" = 123
* "Terran_Missile_Turret" = 124
* "Terran_Bunker" = 125
* "Zerg_Infested_Command_Center" = 130
* "Zerg_Hatchery" = 131
* "Zerg_Lair" = 132
* "Zerg_Hive" = 133
* "Zerg_Nydus_Canal" = 134
* "Zerg_Hydralisk_Den" = 135
* "Zerg_Defiler_Mound" = 136
* "Zerg_Greater_Spire" = 137
* "Zerg_Queens_Nest" = 138
* "Zerg_Evolution_Chamber" = 139
* "Zerg_Ultralisk_Cavern" = 140
* "Zerg_Spire" = 141
* "Zerg_Spawning_Pool" = 142
* "Zerg_Creep_Colony" = 143
* "Zerg_Spore_Colony" = 144
* "Zerg_Sunken_Colony" = 146
* "Zerg_Extractor" = 149
* "Protoss_Nexus" = 154
* "Protoss_Robotics_Facility" = 155
* "Protoss_Pylon" = 156
* "Protoss_Assimilator" = 157
* "Protoss_Observatory" = 159
* "Protoss_Gateway" = 160
* "Protoss_Photon_Cannon" = 162
* "Protoss_Citadel_of_Adun" = 163
* "Protoss_Cybernetics_Core" = 164
* "Protoss_Templar_Archives" = 165
* "Protoss_Forge" = 166
* "Protoss_Stargate" = 167
* "Protoss_Fleet_Beacon" = 169
* "Protoss_Arbiter_Tribunal" = 170
* "Protoss_Robotics_Support_Bay" = 171
* "Protoss_Shield_Battery" = 172
* "Resource_Mineral_Field" = 176
* "Resource_Mineral_Field_Type_2" = 177
* "Resource_Mineral_Field_Type_3" = 178
* "Resource_Vespene_Geyser" = 188
* "Spell_Dark_Swarm" = 202

