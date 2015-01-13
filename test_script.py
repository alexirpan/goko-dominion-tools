from gdt.logparse.gokoparse import *
import argparse

p = argparse.ArgumentParser()
p.add_argument('name')
p.add_argument('--run', dest='run', action='store_const', const=True, default=False)
args = p.parse_args()

"""
lines = open(args.name).read().split('\n')
lines = clean_play_lines(lines)

for line in lines:
    print line
print 1/ 0 
"""

skip = [
    # games with JoaT or Vault in supply
    126,
    151,
    46,
    142,
    180,
    156,
    175,
    18,
    241,
    185,
    194,
    124,
    159,
    250,
    67,
    216,
    200,
    25,
    167,
    11,
    88,
    249,
    140,
    22,
    234,
    192,
    # games with TR or KC in supply
    29,
    157,
    233,
    81,
    225,
    263,
    169,
    248,
    21,
    133,
    13,
    91,
    5,
    183,
    106,
    161,
    224,
    164,
    118,
    184,
    252,
    103,
    80,
    120,
    98,
    78,
    240,
    246,
    247,
    112,
    62,
    7,
    232,
    209,
    144,
    52,
    # games with Prince in supply
    108,
    39,
    60,
    162,
    101,
    150,
    203,
    228,
    18,
    15,
    250,
    260,
]
if args.run:
    passed = 0
    failed = 0
    failing = []
    for i in range(1, 264):
        if i in skip:
            continue
        try:
            generate_game_states(open('testlogs/log%d.txt' % i).read())
            passed += 1
        except:
            failed += 1
            failing.append(i)
    print 'Passed %d out of %d tests' % (passed, failed + passed)
    print 'Failing logs', failing
else:
    game = generate_game_states(open(args.name).read())
