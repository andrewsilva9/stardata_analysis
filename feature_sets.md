## Feature sets for clustering

### MIN:
Bare minimum features. 
* `percent_health`: current_health / max_health
* `current_cooldown`: ground_cd / max_cd
* `distance_from_home`: distance from unit spawn point
* `nearby_allies`: number of allies within 20 units (arbitrary threshold I set)
* `percent_shield`: current_shield / max_shield (only for protoss for now)
- [ ] add nearby enemies?

### MED:
Medium saturated features:
* ALL OF MIN
* SUBSET OF FLAGS: TBD, they are all binary features
* `visible`: binary feature
* `size`: enum 1-3 (1 smallest, 3 largest)
* `armor`: amount of armor?
* `energy`: amount of current energy?

### MAX:
Overwhelming data:
* ALL OF MED
* `type`: unit type
* `ground_damage_type`: enum for damage type
* `air_damage_type`: enum for damage type
* `ground_range`: range for ground attack
* `air_range`: range for air attack

### TASK FEATURES:
For each subset of features, I will also optionally include fine-grained task / action specific information. This means incorporating:
* `order_type`: the enumerated types of each order (see `utils/data_utils.py` for a list of those)
* `order_target`: who am I doing this to?
* `order_target_x`: where am I going in x?
* `order_target_y`: where am I going in y?
* `distance_to_target`: distance from me to the target (x,y) 
