from gdt.logparse.gokoparse import generate_game_states

game = generate_game_states(open('log.txt').read())
