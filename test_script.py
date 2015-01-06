from gdt.logparse.gokoparse import *
import argparse

p = argparse.ArgumentParser()
p.add_argument('name')
args = p.parse_args()

"""
lines = open(args.name).read().split('\n')
lines = clean_play_lines(lines)

for line in lines:
    print line
print 1/ 0 
"""

game = generate_game_states(open(args.name).read())
