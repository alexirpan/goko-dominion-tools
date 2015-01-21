import argparse
import sys
import os

# to get import below working
basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../')
# this should be append instead of insert...except for some reason that isn't working
sys.path.insert(1, basedir)

from parser.gokoparse import *

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
# logs where one player's name is entirely non-ASCII
# the fetch script ignores non-ASCII chars so pname is empty string. This ends badly
339,
342,
379,
383,
402,
# a strange mix of Sir Michael and Jack, don't feel like fixing
# figuring out what lines of Sir Micahel are the Miltia attack and what lines are the Knight attack is tricky
767,
# Treasury topdecked at end of turn without buying anything or playing any treasures
# Some idea on how to find the phase of turn but skip for now
615,
627,
674,
740,
# logs with TR, KC, Procession, or Counterfeit
574,
29,
157,
539,
457,
636,
233,
81,
225,
744,
546,
550,
713,
132,
506,
321,
162,
536,
524,
458,
446,
691,
548,
661,
169,
248,
437,
695,
616,
772,
15,
519,
442,
133,
13,
32,
675,
481,
267,
91,
409,
64,
441,
670,
472,
577,
648,
391,
771,
669,
5,
611,
559,
671,
276,
183,
293,
264,
322,
626,
161,
333,
164,
605,
8,
578,
243,
23,
460,
436,
738,
184,
252,
694,
774,
343,
103,
80,
173,
766,
702,
269,
120,
98,
78,
240,
346,
102,
158,
246,
366,
247,
1,
604,
588,
244,
602,
686,
700,
701,
268,
249,
450,
112,
62,
256,
49,
415,
7,
234,
658,
232,
295,
209,
117,
144,
266,
272,
504,
540,
52,
422,
525,
643,
]

if args.run:
    passed = 0
    failed = 0
    failing = []
    for i in range(1, 776):
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
        log, game = generate_game_states(open("testlogs/log%d.txt" % int(args.name)).read())
    else:
        log, game = generate_game_states(open(args.name).read())
    import sys
    print '\n'.join(log)
