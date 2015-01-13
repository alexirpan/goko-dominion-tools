# Base modules
import re
import datetime
import sys

# Project modules
#from gdt.model import db_manager
from gdt.model.constants import *
from gdt.model.domgame import GameResult
from gdt.model.domgame import PlayerResult
from gdt.model.domgame import GainRet


# Regular expressions used to parse goko logs.  Precompiled for speed.
RE_RATING = re.compile('Rating system: (.*)')
RE_SUPPLY = re.compile('[sS]upply cards: (.*)')
RE_COMMA = re.compile(', ')
RE_STARTC = re.compile('(.*) - starting cards: (.*)')
RE_TURNX = re.compile('--* (.*): turn ([0-9]*) ([posessed] )?--*')
RE_GAINS = re.compile('(.*) \- gains (.*)')
RE_RETS = re.compile('(.*) \- returns (.*) to')
RE_VPS = re.compile('(.*) - total victory points: (-?\d*)')
RE_NTURNS = re.compile('(.*) - turns: (\d*)')
RE_QUIT = re.compile('(.*) - quit')
RE_RESIGN = re.compile('(.*) - resigned')
RE_PLACE = re.compile('([0-9]).. place: (.*)')
RE_GUEST = re.compile('^guest.*', re.IGNORECASE)
RE_GAMEOVER = re.compile('--* Game Over --*')

# Regex added for replay system

RE_DRAWS = re.compile('(.*) \- draws (.*)$')
RE_PLAYS = re.compile('(.*) \- plays ([^\(]*)$')
RE_ANNOTATED_PLAYS = re.compile('(.*) \- plays ([^\(]*) \(.*\)$')
RE_TREASURE_PLAYS = re.compile('(.*) \- plays [0-9] .*$')
RE_DISCARDS = re.compile('(.*) \- discards (.*)$')
# This is used when discarding your entire hand, or when
# revealed cards need to be discarded
RE_DISCARDS_MULTIPLE = re.compile('(.*) \- discards: (.*)$')
RE_SHUFFLES = re.compile('(.*) \- shuffles deck$')
# need this to catch multiple Alchemist case
RE_TOPDECKS = re.compile('(.*) - places ([^,]*) on top of deck$')
RE_TRASHES = re.compile('(.*) \- trashes (.*)$')
RE_PASSES = re.compile('(.*) \- passes (.*)$')
RE_RETURN_TO_SUPPLY = re.compile('(.*) \- returns (.*) to the Supply$')
RE_SETS_ASIDE = re.compile('(.*) \- sets aside (.*)$')
# Reveal for current player only, like Cartographer
RE_LOOKS_AT = re.compile('(.*) \- looks at (.*)$')
RE_REVEALS = re.compile('(.*) \- reveals: (.*)$')
RE_REVEALS2 = re.compile('(.*) \- reveals (.*)$')
# Haven edge case (must be checked before edge case below)
RE_HAVEN_DURATION = re.compile('(.*) \- places set aside (.*) in hand$')
# wording for Hunting Party, Wishing Well, Farming Village, etc
RE_PLACES_IN_HAND = re.compile('(.*) \- places (.*) in hand$')
# Library edge case (urrrgh)
RE_MOVES_TO_HAND = re.compile('(.*) \- moves (.*) to hand$')
# This wording is used when multiple revealed cards are put into
# your hand. Examples are Adventurer, Scout. Oddly enough, not Apothecary
# Apothecary doesn't log which cards go into your hand, despite using the
# exact same kind of logic as Scout. Sighhhh
RE_PLACE_MULTIPLE_IN_HAND = re.compile('(.*) \- places cards in hand: (.*)$')
RE_NATIVE_VILLAGE_PULL = re.compile('(.*) \- takes set aside cards: (.*)$')
RE_REACTION = re.compile('(.*) \- reveals reaction (.*)$')
RE_DURATION = re.compile('(.*) \- duration (.*)$')
RE_BUYS = re.compile('(.*) \- buys (.*)$')
RE_WATCHTOWER = re.compile('(.*) \- applied Watchtower to (.*)$')

# play line annotations
TR_ANN = " (Throne Room)"
KC_ANN = " (King's Court)"
HERALD_ANN = " (Herald)"
PROCESSION_ANN = " (Procession)"
COUNTERFEIT_ANN = " (Counterfeit)"
GOLEM_ANN = " (Golem)"
VENTURE_ANN = " (Venture)"
ANNOTATIONS = [TR_ANN, KC_ANN, HERALD_ANN, PROCESSION_ANN, COUNTERFEIT_ANN, GOLEM_ANN, VENTURE_ANN]


# TODO: fix this
# advopps = db_manager.get_advbot_names()
advopps = []


class WrongPlacesException(Exception):
    pass


class TurnCountException(Exception):
    pass


class ParseException(Exception):
    pass


def scores_to_ranks(scores):
    ranks = [0] * len(scores)
    for i in range(len(scores)):
        larger = set()
        for j in range(len(scores)):
            if scores[j] > scores[i]:
                larger.add(scores[j])
        ranks[i] = len(larger) + 1
    return(ranks)

# helper function for clean_play_lines, DO NOT CALL ELSEWHERE
def read_til_resolved(lines):
    # quick sanity check
    # this can happen if the last action played is a giant TR chain, with
    # no other actions in hand to copy
    if not lines:
        return []
    # make sure the while loop runs at least once
    line = lines[0]
    m = RE_PLAYS.match(line)
    player, card = m.group(1), m.group(2)
    lines[:1] = []

    # TODO handle Herald
    # TODO handle Prince
    # TODO handle Procession/Counterfeit differently
    if card == "Throne Room" or card == "Procession" or card == "Counterfeit":
        # check the next line to make sure it's an action by the same player
        # this handles the edge case where someone plays Throne Room,
        # but doesn't have any actions in hand to copy
        # (might not handle all of it)
        m = RE_PLAYS.match(lines[0])
        next_player, next_card = m.group(1), m.group(2)
        if next_player != player:
            return [line]
        if next_card not in CARDNAME_TO_TYPE:
            return [line]
        cardtype = CARDNAME_TO_TYPE[next_card]
        if 'action' not in cardtype.split('-'):
            return [line]

        first_play = read_til_resolved(lines)
        second_play = read_til_resolved(lines)
        # first line of 2nd play is extra, but we need to make sure there is a first line
        if second_play:
            second_play[0] += TR_ANN
        return [line] + first_play + second_play
    elif card == "King's Court":
        # again check same thing as TR
        m = RE_PLAYS.match(lines[0])
        next_player, next_card = m.group(1), m.group(2)
        if next_player != player:
            return [line]
        if next_card not in CARDNAME_TO_TYPE:
            return [line]
        cardtype = CARDNAME_TO_TYPE[next_card]
        if 'action' not in cardtype.split('-'):
            return [line]
        # TODO account for KC being optional
        # (distinguish between KC-action, action, and KC choose nothing, action, action)
        first_play = read_til_resolved(lines)
        second_play = read_til_resolved(lines)
        third_play = read_til_resolved(lines)
        # same logic, first line of 2nd and 3rd plays are extra
        if second_play:
            second_play[0] += KC_ANN
        if third_play:
            third_play[0] += KC_ANN
        return [line] + first_play + second_play + third_play
    elif card == "Golem":
        # both plays are from the revealed cards, so ignore the first line of both
        # UNTESTED AND UNREFINED
        first_play = read_til_resolved(lines)
        second_play = read_til_resolved(lines)
        if first_play:
            first_play[0] += GOLEM_ANN
        if second_play:
            second_play[0] += GOLEM_ANN
        return [line] + first_play + second_play
    elif card == "Venture":
        # TODO account for when Venture doesn't find a treasure
        # the next played card comes from revealed cards and is ignorable
        next_play = read_til_resolved(lines)
        if next_play:
            next_play[0] += VENTURE_ANN
        return [line] + next_play
    else:
        return [line]

def clean_play_lines(log_lines):
    # return the log with all "plays X" lines annotated
    # This lets us figure out what "plays X" lines need to move cards from the hand and which don't
    # to do this, we first create a list of all lines that are of the form "X plays Y"
    # this gets passed to the helper function which annotates which lines to keep
    # then, go back to the original log and apply these annotations
    # ideally, the method would operaate on the original log, instead of needing
    # a sanitized version. Implement that if this becomes a bottleneck?
    all_play_lines = [line for line in log_lines if RE_PLAYS.match(line)]
    annotated = []
    while all_play_lines:
        # read_til_resolved returns a new list with annotations
        annotated.extend(read_til_resolved(all_play_lines))
    cleaned = []
    for line in log_lines:
        if not RE_PLAYS.match(line):
            cleaned.append(line)
        else:
            cleaned.append(annotated[0])
            annotated[:1] = []
    return cleaned

def get_cards_drawn(line):
    line = line[line.rfind('-'):]
    # Remove "- draws "
    line = line[8:]
    return line.split(', ')

def get_cards_trashed(line):
    line = line[line.rfind('-'):]
    # Remove "- trashes "
    line = line[10:]
    return line.split(', ')

def find_cleanup_phase_hands(log_lines):
    # Okay so dealing with this is just so annoying
    # the only way to differentiate hands drawn during cleanup is by where they are
    # in the log, and there may be extraneous shuffle messages in the way too
    # So to avoid dealing with that nonsense, preprocess all of it here
    # This means we do another pass over the entire log text but that
    # should be negligible compared to network times
    # If you want to try to fit this into the other code, feel free...

    # a list of the hands the next player draws during cleanup
    # should handle Outpost, may not handle Possession
    hands_for_each_turn = []
    lines_to_remove = []
    turn_line_indices = [i for i, line in enumerate(log_lines) if RE_TURNX.match(line)]
    # skip the very first turn line (this is handled in the starting hands section
    for ind in turn_line_indices[1:]:
        cards = []
        # we only expect to see draws or shuffles
        start = ind - 1
        while True:
            line = log_lines[start]
            m = RE_DRAWS.match(line)
            if m:
                pname = m.group(1)
                cards.extend(get_cards_drawn(line))
                if len(cards) == 5:
                    break
            elif RE_SHUFFLES.match(line):
                pass
            else:
                break
            start -= 1
        lines_to_remove.append( (start, ind) )
        hands_for_each_turn.append( (pname, cards, log_lines[start:ind]) )
    cleaned = []
    curr = 0
    for start, end in lines_to_remove:
        cleaned.extend(log_lines[curr:start])
        curr = end
    cleaned.extend(log_lines[curr:])
    log_lines[:] = cleaned
    return hands_for_each_turn


class GameState:
    # holds all the needed data and some extra methods
    WILD = "WILDCARD"

    def __init__(self, pCount, playerInd):
        self.playerInd = playerInd
        self.pCount = pCount
        self.player_hands = [ [] for _ in range(self.pCount) ]
        self.last_card_played = None
        self.played_by = None
        self.last_card_bought = None
        self.bought_by = None
        self.revealed_reaction = None
        self.revealed_by = None
        self.debug = True
        self.phase = 'action'

    def player_index(self, pname):
        return self.playerInd[pname]

    def add_to_hand(self, pname, card):
        self.player_hands[self.player_index(pname)].append(card)

    def handle_treasure_case(self, pname, line):
        line = line[line.rfind('-'):]
        # Remove "- plays "
        line = line[8:]
        treasure_names_and_num = line.split(', ')
        for token in treasure_names_and_num:
            num, cardname = token.split(' ', 1)
            self.set_last_card_played(pname, cardname)
            num = int(num)
            for _ in range(num):
                self.remove_from_hand(pname, cardname)

    def add_wild(self, pname):
        self.add_to_hand(pname, GameState.WILD)

    def draw_cleanup_hand(self, pname, hand):
        self.player_hands[self.player_index(pname)] = hand

    def get_hand(self, pname):
        return self.player_hands[self.player_index(pname)]

    def remove_from_hand(self, pname, card):
        # disambiguating TR/KC chains isn't always possible
        # may have to ignore some Tr/KC removals later on, but ValueErrors are good bug signals
        lst = self.player_hands[self.player_index(pname)]
        if GameState.WILD in lst:
            try:
                lst.remove(card)
            except ValueError:
                lst.remove(GameState.WILD)
        elif self.debug:
            lst.remove(card)
        else:
            if card in lst:
                lst.remove(card)

    def set_last_card_played(self, pname, card):
        self.last_card_played = card
        self.played_by = pname
        self.last_card_bought = None
        self.bought_by = None
        self.revealed_reaction = None
        self.revealed_by = None
        if 'treasure' in CARDNAME_TO_TYPE[card]:
            self.phase = 'buy'
        else:
            self.pahse = 'action'

    def set_last_card_bought(self, pname, card):
        self.last_card_played = None
        self.played_by = None
        self.last_card_bought = card
        self.bought_by = pname
        self.revealed_reaction = None
        self.revealed_by = None

    def set_revealed_reaction(self, pname, card):
        # Don't want to set rest to anything else
        self.revealed_reaction = card
        self.revealed_by = pname


def generate_game_states(logtext):
    # until I'm sure this code works, placing all replay system code
    # at the end in an easy-to-comment-out block

    # copy pasted pre-processing
    # Parse various info from each player's starting cards
    # NOTE: Names are ordered alphabetically, not by order of play
    log_lines = logtext.split("\n")
    startcl = []
    turnl = []

    pnames = set()
    playerInd = dict()
    pCount = 0
    for line in log_lines:
        m = RE_STARTC.match(line)
        if m:
            startcl.append(m)
        m = RE_TURNX.match(line)
        if m:
            turnl.append(m)
    for m in startcl:
        pname = m.group(1)

        # Count number of players
        pCount += 1

        # Don't parse games with duplicate bot names
        if pname in pnames:
            raise ParseException('Duplicate name: %s' % (pname))
        else:
            pnames.add(pname)

    ## GAME TURNS ##
    # Parse turn numbers to obtain player names, order, and turns taken
    iOrder = 0
    for m in turnl:
        pname = m.group(1)
        turn_num = int(m.group(2))
        if turn_num == 1:
            playerInd[pname] = iOrder
            iOrder += 1
            if iOrder == pCount:
                break

    # log with all extra whitespace/lines removed
    log_lines = [line.strip() for line in log_lines if line.strip()]

    state = GameState(pCount, playerInd)

    # handles initializing starting hands for each player
    start_hands_processed = 0
    for i, line in enumerate(log_lines):
        m = RE_DRAWS.match(line)
        if RE_DRAWS.match(line):
            pname = m.group(1)
            state.draw_cleanup_hand(pname, get_cards_drawn(line))
            start_hands_processed += 1
            if start_hands_processed == pCount:
                log_lines = log_lines[i+1:]
                break
    # finds starting hands for every other turn, removing the extra lines from the log
    # TODO Right now I believe this removes shuffle message as well. Fix?
    # Best way to do this may be to add a line saying "discards hand for cleanup"
    # instead of doing this manual check
    hands_for_next_turn = find_cleanup_phase_hands(log_lines)

    # remove extra play lines for TR/KC
    log_lines = clean_play_lines(log_lines)

    # TODO this is the same structure as the above code (continue at the end of every case)
    # Someone this design feels clunky but I can't think of anything better right now?
    for line, next_line in zip(log_lines, log_lines[1:]):
        # debug printing
        for name in pnames:
            print name
            print state.get_hand(name)
        print 'Next line to parse: ', line
        print ' '

        # draw line is opening hand if the next line describes the next turn
        # TODO some annoying Possession edge case?
        m = RE_TURNX.match(next_line)
        if m:
            # TODO remove the skipped lines part after this works
            pname, next_hand, skipped_lines = hands_for_next_turn[0]
            state.draw_cleanup_hand(pname, next_hand)
            # remove first element of list
            hands_for_next_turn[0:1] = []
            print '    Applying the following cleanup lines:'
            print ''.join('    ' + line + '\n' for line in skipped_lines)
            continue
        m = RE_TREASURE_PLAYS.match(line)
        if m:
            # This doesn't need to update state.last_card_played since
            # the play treasures buttons only plays treasures with no side effects
            pname = m.group(1)
            state.handle_treasure_case(pname, line)
            continue
        m = RE_PLAYS.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.set_last_card_played(pname, card)
            state.remove_from_hand(pname, card)
            continue
        m = RE_ANNOTATED_PLAYS.match(line)
        if m:
            # update the state but don't try to move the card
            pname = m.group(1)
            card = m.group(2)
            state.set_last_card_played(pname, card)
            continue
        m = RE_BUYS.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.set_last_card_bought(pname, card)
            state.phase = 'buy'
            continue
        m = RE_DISCARDS_MULTIPLE.match(line)
        if m and state.last_card_played not in DISCARD_FROM_REVEAL and state.last_card_bought not in DISCARD_ON_BUY:
            pname = m.group(1)
            line = line.rsplit(":", 1)[1]
            cards = [card.strip() for card in line.split(",")]
            for card in cards:
                state.remove_from_hand(pname, card)
            continue
        m = RE_DISCARDS.match(line)
        if m and state.last_card_played not in DISCARD_FROM_REVEAL and state.last_card_bought not in DISCARD_ON_BUY:
            pname = m.group(1)
            card = m.group(2)
            state.remove_from_hand(pname, card)
            continue
        m = RE_TOPDECKS.match(line)
        # current phase is not very robust so odds are bugs are here
        if m and state.last_card_played not in TOPDECKS_FROM_REVEAL and state.last_card_played not in TOPDECKS_FROM_PLAY and state.last_card_bought not in TOPDECKS_ON_BUY and state.phase == 'action':
            pname = m.group(1)
            card = m.group(2)
            state.remove_from_hand(pname, card)
            continue
        m = RE_DRAWS.match(line)
        if m:
            pname = m.group(1)
            for card in get_cards_drawn(line):
                state.add_to_hand(pname, card)
            continue
        m = RE_TRASHES.match(line)
        if m:
            pname = m.group(1)
            cards = get_cards_trashed(line)
            trash_from_hand = state.last_card_played not in TRASHES_FROM_PLAY and state.last_card_played not in TRASHES_FROM_REVEAL and state.last_card_bought not in TRASHES_ON_BUY and state.revealed_reaction != 'Watchtower'
            if trash_from_hand:
                # the TM in play is always trashed, so remove one from the list
                if state.last_card_played == 'Treasure Map':
                    cards.remove('Treasure Map')

                for card in cards:
                    if card != 'Fortress':
                        state.remove_from_hand(pname, card)
            else:
                # handle on-trash effects
                for card in cards:
                    if card == 'Fortress':
                        # not trashed from the hand, so we need to put it back
                        state.add_to_hand(pname, 'Fortress')
                    elif card == 'Overgrown Estate':
                        # doesn't log what card is drawn
                        state.add_wild(pname)
            continue
        m = RE_HAVEN_DURATION.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.add_to_hand(pname, card)
            continue
        m = RE_PLACE_MULTIPLE_IN_HAND.match(line)
        if m:
            pname = m.group(1)
            # get cards to put in hand
            line = line.rsplit(":", 1)[-1]
            cards = [card.strip() for card in line.split(",")]
            for card in cards:
                state.add_to_hand(pname, card)
            continue
        m = RE_PLACES_IN_HAND.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.add_to_hand(pname, card)
            continue
        m = RE_MOVES_TO_HAND.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.add_to_hand(pname, card)
            continue
        m = RE_GAINS.match(line)
        if m and state.last_card_played in GAIN_TO_HAND:
            pname = m.group(1)
            card = m.group(2)
            state.add_to_hand(pname, card)
            continue
        m = RE_PASSES.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.remove_from_hand(pname, card)
            # clean me up later
            next_player_ind = (playerInd[pname] + 1) % pCount
            for p in playerInd:
                if playerInd[p] == next_player_ind:
                    next_player = p
                    state.add_to_hand(next_player, card)
                    break
            continue
        m = RE_RETURN_TO_SUPPLY.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.remove_from_hand(pname, card)
            continue
        m = RE_SETS_ASIDE.match(line)
        if m and state.last_card_played not in SETS_ASIDE_FROM_DECK:
            pname = m.group(1)
            card = m.group(2)
            state.remove_from_hand(pname, card)
            continue
        m = RE_NATIVE_VILLAGE_PULL.match(line)
        if m:
            pname = m.group(1)
            line = line.rsplit(":", 1)[1]
            cards = [card.strip() for card in line.split(",")]
            for card in cards:
                state.add_to_hand(pname, card)
        m = RE_REVEALS.match(line)
        if m and state.last_card_played == 'Apothecary':
            # Apothecary Copper pulling is not listed in the log
            pname = m.group(1)
            line = line.rsplit(":", 1)[1]
            cards = [card.strip() for card in line.split(",")]
            for card in cards:
                if card == "Copper" or card == "Potion":
                    state.add_to_hand(pname, card)
            continue
        m = RE_REVEALS2.match(line)
        if m and state.last_card_played == 'Scrying Pool':
            # Neither is Scrying Pool
            pname = m.group(1)
            if pname != state.played_by:
                continue
            line = line[line.index("- reveals")+9:]
            cards = [card.strip() for card in line.split(",")]
            for card in cards:
                state.add_to_hand(pname, card)
            continue
        m = RE_REACTION.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.set_revealed_reaction(pname, card)
            if card == 'Horse Traders':
                state.remove_from_hand(pname, card)
            continue
        m = RE_DURATION.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            if card == 'Horse Traders':
                state.add_to_hand(pname, card)
            continue
        # Watchtower topdeck is not handled for now
        # TODO implement it
        m = RE_WATCHTOWER.match(line)
        if m:
            pname = m.group(1)
            state.set_revealed_reaction(pname, 'Watchtower')
            continue

# Parse a game log.  Create and return the resulting GameResult object
def parse_goko_log(logtext):

    # First just sort the log lines.  This doubles the regex matching we have
    # to do, but it keeps the code cleaner.
    supplyl, ratingl = (None, None)
    startcl, turnl, gainl, retl = ([], [], [], [])
    vpl, nturnl, quitl, placel = ([], [], [], [])
    resignl = []
    gains = []
    rets = []

    cur_turn = None
    cur_player = None

    first_quit_line = None
    first_quitter = None
    num_quitters = 0

    game_over_line = None
    line_number = 0
    for line in logtext.split('\n'):
        line_number += 1

        m = RE_SUPPLY.match(line)
        if m:
            supplyl = m
            continue
        m = RE_RATING.match(line)
        if m:
            ratingl = m
            continue
        m = RE_STARTC.match(line)
        if m:
            startcl.append(m)
            continue
        m = RE_TURNX.match(line)
        if m:
            turnl.append(m)
            if not m.group(3):
                cur_player = m.group(1)
                cur_turn = int(m.group(2))
            continue
        m = RE_GAINS.match(line)
        if m:
            pname = m.group(1)
            cname = m.group(2)
            if cname in RUINSES:
                cpile = 'Ruins'
            elif cname in KNIGHTS:
                cpile = 'Knight'
            else:
                cpile = cname
            gains.append(GainRet(cname, cpile, cur_player, cur_turn))
            continue
        m = RE_RETS.match(line)
        if m:
            pname = m.group(1)
            cname = m.group(2)
            if cname in RUINSES:
                cpile = 'Ruins'
            elif cname in KNIGHTS:
                cpile = 'Knight'
            else:
                cpile = cname
            rets.append(GainRet(cname, cpile, cur_player, cur_turn))
            continue
        m = RE_VPS.match(line)
        if m:
            vpl.append(m)
            continue
        m = RE_NTURNS.match(line)
        if m:
            nturnl.append(m)
            continue
        m = RE_RESIGN.match(line)
        if m:
            resignl.append(m)
            continue
        m = RE_QUIT.match(line)
        if m:
            quitl.append(m)
            first_quit_line = (first_quit_line
                               if first_quit_line
                               else line_number)
            first_quitter = m.group(1)
            num_quitters += 1
            continue
        m = RE_GAMEOVER.match(line)
        if m:
            game_over_line = line_number
            continue
        m = RE_PLACE.match(line)
        if m:
            placel.append(m)
            continue

    # Game data to be parsed
    supply = []       # List of supply cards
    rating = None     # Rating system used, if available
    presults = {}       # player name --> player game info

    # Game metadata to be parsed
    shelters = False
    guest = False
    bot = False
    pCount = 0
    colony = False
    adventure = False

    ## PRE-GAME SETUP ###

    # Parse supply
    for cname in RE_COMMA.split(supplyl.group(1)):
        if cname in RUINSES:
            cname = 'Ruins'
        elif cname in KNIGHTS:
            cname = 'Knight'
        if cname == 'Colony':
            colony = True
        supply.append(cname)

    # Parse rating system (not available for pre-May logs)
    if ratingl:
        rating = ratingl.group(1)

    # Parse various info from each player's starting cards
    # NOTE: Names are ordered alphabetically, not by order of play
    for m in startcl:
        pname = m.group(1)
        scards = RE_COMMA.split(m.group(2))

        # Count number of players
        pCount += 1

        # Determine whether a guest is playing
        if RE_GUEST.match(pname):
            guest = True

        # Determine whether a bot is playing
        for bname in BOT_NAMES:
            if pname.startswith(bname):
                bot = True

        # Determine whether this is an adventure
        if pname in advopps:
            adventure = True

        # Determine shelters or estates
        if len(set(['Hovel', 'Overgrown Estate', 'Necropolis']) & set(scards)):
            shelters = 1

        # Don't parse games with duplicate bot names
        if pname in presults:
            raise ParseException('Duplicate name: %s' % (pname))
        else:
            presults[pname] = PlayerResult(pname)

    ## GAME TURNS ##
    #
    # Parse turn numbers to obtain player names, order, and turns taken
    iOrder = 0
    for m in turnl:
        pname = m.group(1)
        turn_num = int(m.group(2))
        presults[pname].turns = turn_num
        if presults[pname].order is None:
            iOrder += 1
            presults[pname].order = iOrder

    ## POST GAME ##

    # Total VPs
    for m in vpl:
        pname = m.group(1)
        vps = int(m.group(2))
        presults[pname].vps = vps

    # Parse resignations
    someoneResigned = False
    for m in resignl:
        pname = m.group(1)
        presults[pname].resign = True
        someoneResigned = True

    # Parse quits
    someoneQuit = False
    for m in quitl:
        pname = m.group(1)
        presults[pname].quit = True
        someoneQuit = True

    # Number of turns taken
    wrongTurnCounts = False
    for m in nturnl:
        pname = m.group(1)
        turns = int(m.group(2))
        p = presults[pname]
        if not turns == p.turns:
            # Note: Goko counts turns incorrectly sometimes, and i can't figure
            # out why. I'm ignoring their count and using my own.
            wrongTurnCounts = True
            pass

            # My past notes/code on the same error:
            # Note: Goko counts turns incorrectly with outpost.  This may have
            # led to some incorrect game results.  I'm ignoring it.
            #if (someoneQuit or someoneResigned or ('Outpost' in supply)):
            #    p.turns = turns
            #else:
            #    #print(someoneQuit)
            #    #print(someoneResigned)
            #    raise TurnCountException()

    # Calculate players' places/ranks
    # Note: I'm counting on there having been fewer than 1000 turns and
    #       no more than 99 curses (or other negative VPs). :)
    pnames = []
    scores = []
    for pname in presults:
        p = presults[pname]
        score = p.vps*1000 - p.turns  # Account for vps and turns taken
        if presults[pname].quit or presults[pname].resign:
            score = -99999
        pnames.append(pname)
        scores.append(score)
    ranks = scores_to_ranks(scores)
    for i in range(len(pnames)):
        presults[pnames[i]].rank = ranks[i]

    # Search & verify places/ranks. There are many ways that Goko screws up
    # ranking at the end of the game. I'm trusting my own rankings over theirs
    # whenever I can roughly determine that the error is one that they make
    # consistently.
    for m in placel:
        pname = m.group(2)
        place = int(m.group(1))
        if (presults[pname].rank != place):
            if presults[pname].rank != place:
                if (len(placel) > pCount):
                    # Ignore a Goko bug where player ranks were listed twice
                    # (with different results)
                    print('Places listed twice.')
                elif (wrongTurnCounts):
                    print('Goko miscounted number of turns')
                elif (first_quit_line == game_over_line + 1):
                    # Ignore a Goko bug where the "quit" shows up after the
                    # game over log messages
                    print('Playerquit-gameend race condition.')
                elif someoneQuit and len(presults) >= 3:
                    # Ignore a Goko bug where a player quitting screws up the
                    # ordering of the other players
                    print('Quit screwed up opponent rankings')
                elif presults[pname].turns < 2:
                    # Ignore a Goko bug where games that never really start end
                    # up with the wrong places.
                    print('Wrong rankings in <2 turn game')
                elif num_quitters > 1:
                    # Ignore a Goko bug where when both players quit, the loser
                    # is the player whose turn it was
                    print('Wrong rankings with 2+ quitters') 
                else:
                    print(presults)
                    print(pname, place)
                    raise WrongPlacesException()

    return GameResult(supply, gains, rets, rating, shelters, guest, bot,
                      pCount, colony, presults, adventure)

# For testing
# Usage: ./gokoparse.py [logfile]
if __name__ == "__main__":
    #x = scores_to_ranks([1, 4, 3, 3])
    #print(x)
    logfile = sys.argv[-1]
    g = parse_goko_log(open(logfile).read())
    print(g)
