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

if args.run:
    passed = 0
    failed = 0
    failing = []
    for i in range(1, 264):
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
