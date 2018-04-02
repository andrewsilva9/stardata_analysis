# Created by Andrew Silva on 3/30/18

from torchcraft import replayer
import glob

# python port of the cpp script for getting corrupted replays
# best I can tell it is the same?
input_pattern = '/media/asilva/HD_home/StarData/dumped_replays/**/*.tcr'
all_files = glob.glob(input_pattern)
bad_files = []
for filename in all_files:
    try:
        rep = replayer.load(filename)
        ore = 0
        gas = 0
        used_ore = 0
        used_gas = 0
        for i in range(len(rep)):
            frame = rep.getFrame(i)
            cur_ore = 0
            cur_gas = 0
            res = frame.resources
            for r in res.values():
                cur_ore += r.ore
                cur_gas += r.gas
            if i > len(rep) / 2:
                used_ore += max(0, ore - cur_ore)
                used_gas += max(0, gas - cur_gas)
            ore = cur_ore
            gas = cur_gas
        percent_used_ore = 1.0*used_ore / (used_ore + ore)
        percent_used_gas = 1.0*used_gas / (used_gas + gas)
        if (percent_used_gas + percent_used_ore) / 2.0 < 0.7:
            print(filename + " is corrupt")
            bad_files.append(filename)
    except Exception as e:
        print("Exception :(")
        print(e)
        bad_files.append(filename)
        continue
with open('bad_files.txt', 'wb') as outfile:
    for line in bad_files:
        outfile.write(line)
        outfile.write('\n')
    outfile.flush()
    outfile.close()
