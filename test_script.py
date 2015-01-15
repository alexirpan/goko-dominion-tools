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
    # games with Procession or Counterfeit in supply
    # (need to overhaul the annotation system to handle these cases)
    233,
    132,
    162,
    143,
    248,
    150,
    15 ,
    32 ,
    64 ,
    8 ,
    74 ,
    243,
    23 ,
    178,
    173,
    102,
    158,
    2 ,
    1 ,
    244,
    249,
    256,
    49 ,
    234,
    260,
    117,
    # games with Hermit or Urchin (weird trash conditions)
    72,
    39,
    163,
    69,
    63,
    228,
    254,
    15,
    198,
    96,
    185,
    127,
    8,
    74,
    251,
    50,
    95,
    1,
    231,
    83,
    22,
    93,
    232,
    144,
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
    import re
    if re.compile("[0-9]+").match(args.name):
        game = generate_game_states(open("testlogs/log%d.txt" % int(args.name)).read())
    else:
        game = generate_game_states(open(args.name).read())
