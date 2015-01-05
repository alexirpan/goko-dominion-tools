from gdt.logparse.gokoparse import *
import argparse

p = argparse.ArgumentParser()
p.add_argument('name')
args = p.parse_args()

lines = open(args.name).read().split('\n')
lines = [line for line in lines if RE_PLAYS.match(line)]

for line in lines:
    print line
print 1/ 0 

while lines:
    print read_til_resolved(lines)

# game = generate_game_states(open(args.name).read())
