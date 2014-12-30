from gdt.logparse.gokoparse import generate_game_states
import argparse

p = argparse.ArgumentParser()
p.add_argument('name')
args = p.parse_args()

game = generate_game_states(open(args.name).read())
