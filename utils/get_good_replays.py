# Created by Andrew Silva on 4/2/18
# This file depends on you having already run `get_corrupted_replays.py` because it needs `bad_files.txt`
import glob

input_pattern = '/media/asilva/HD_home/StarData/dumped_replays/**/*.tcr'
all_files = glob.glob(input_pattern)
bad_files = open('bad_files.txt', 'r').readlines()
for i in range(len(bad_files)):
    bad_files[i] = bad_files[i].split('\n')[0]
good_files = []
for file in all_files:
    if file in bad_files:
        continue
    else:
        good_files.append(file)


print("Out of a total " + str(len(all_files)) + " replays")
print("There are " + str(len(bad_files)) + " corrupt replays")
print("So math says there should be " + str(len(all_files) - len(bad_files)) + " clean replays")
print("There are " + str(len(good_files)) + " clean replays")

with open('good_files.txt', 'wb') as outfile:
    for line in good_files:
        outfile.write(line)
        outfile.write('\n')
    outfile.flush()
    outfile.close()
