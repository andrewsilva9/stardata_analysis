## Utils

So this directory has grown a bit unwiedly, therefore this readme should help.

### get_corrupted_replays.py

This is a port of the get_corrupted_replays.cpp that comes with StarData. That file wasn't working for me because of some version mismatches, so I translated it to python and now it works well enough. It generates the `bad_files.txt`, which is a list of replays that are considered corrupt.

### get_good_replays.py

This utilizes `get_corrupted_replays.py` and specifically `bad_files.txt` to generate a .txt of all clean replays: `good_files.txt`. To get that txt, either just copy the one in this repo, or run:
```
$ python get_corrupted_replays.py
$ python get_good_replays.py
```

### data_utils.py

This is one of the more important files. It has the mappings from unit type numbers to names, and order type numbers to names, as well as a couple of functions to do those mappings for you.

### generate_LDA_matrices.py

This was intended to generate matrices of games, where units are documents and orders are words. It's a bit weird, I know, but the idea is that you have a matrix that is full of rows of units. Each unit is then a vector of counts of orders, so each time it has a certain order in a game, that count goes up. This file generates a pickle output.

### generate_n_games_pkl.py

As the title suggests, this generates data for "n" games and outputs it to a pickle. Currently it will either try to find unique units across "n" games (rarely used or useful functionality), or create a temporally continuous array for each game and save that.

### generate_unit_base_pkl.py

This is the same functionality as the useless one in `generate_n_games_pkl.py`. So you can safely ignore it.

### visualize_unit_movement.py

This is the really cool one! Creates a blank image and then paints on units for each frame. It is set to ignore buildings for now, and it also generates some information that it doesn't need to, so it takes a bit longer. It can save videos for later viewing, or just play it back live.
