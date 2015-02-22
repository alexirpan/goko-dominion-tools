# Base modules
import re
import datetime
import sys
import copy
from collections import Counter

# Project modules
from parser.dtconstants import *


# Regular expressions used to parse goko logs.  Precompiled for speed.
RE_RATING = re.compile('Rating system: (.*)')
RE_SUPPLY = re.compile('[sS]upply cards: (.*)')
RE_COMMA = re.compile(', ')
RE_STARTC = re.compile('(.*) - starting cards: (.*)')
RE_TURNX = re.compile('--* (.*): turn ([0-9]*) (\[possessed\] )?--*')
RE_GAINS = re.compile('(.*) \- gains (.*)$')
RE_RETS = re.compile('(.*) \- returns (.*) to')
RE_VPS = re.compile('(.*) - total victory points: (-?\d*)')
RE_NTURNS = re.compile('(.*) - turns: (\d*)')
RE_QUIT = re.compile('(.*) - quit')
RE_RESIGN = re.compile('(.*) - resigned')
RE_PLACE = re.compile('([0-9]).. place: (.*)')
RE_GUEST = re.compile('^guest.*', re.IGNORECASE)
RE_GAMEOVER = re.compile('--* Game Over --*')

# Regex added for replay system

RE_GAINS_TO_TOP = re.compile('(.*) \- gains (.*) to top of deck$')
RE_DISCARDS_FROM_HAND = re.compile('(.*) \- discards (.*) from hand$')
RE_TRASHES_FROM_HAND = re.compile('(.*) \- trashes (.*) from hand$')
RE_TRASHES_FROM_PLAY = re.compile('(.*) \- trashes (.*) from play$')
RE_DRAWS = re.compile('(.*) \- draws (.*)$')
RE_ANNOTATED_PLAYS = re.compile('(.*) \- plays ([^\(]*) \(.*\)$')
RE_TREASURE_PLAYS = re.compile('(.*) \- plays [0-9]+ .*$')
RE_DISCARDS = re.compile('(.*) \- discards (.*)$')
# This is used when discarding your entire hand, or when
# revealed cards need to be discarded
RE_DISCARDS_MULTIPLE = re.compile('(.*) \- discards: (.*)$')
RE_SHUFFLES = re.compile('(.*) \- shuffles deck$')
RE_SHUFFLES_REVEAL = re.compile('(.*) \- shuffles deck \(shuffle for reveal\)$')
# need this to catch multiple Alchemist case
RE_TOPDECKS = re.compile('(.*) - places ([^,]*) on top of deck$')
RE_TOPDECKS_MULTIPLE = re.compile('(.*) \- places (.*,.*) on top of deck$')
RE_TRASHES = re.compile('(.*) \- trashes ([^\(]*)$')
RE_ANNOTATED_TRASH = re.compile('(.*) \- trashes ([^\{]*) \(.*\)$')
RE_PASSES = re.compile('(.*) \- passes (.*)$')
RE_RETURN_TO_SUPPLY = re.compile('(.*) \- returns (.*) to the Supply$')
RE_SETS_ASIDE = re.compile('(.*) \- sets aside ([^\(]*)$')
# Reveal for current player only, like Cartographer
# These are messy. There's probably a better way to do this.
# The reveals hand regex must be checked first
RE_LOOKS_AT = re.compile('(.*) \- looks at (.*)$')
RE_REVEALS = re.compile('(.*) \- reveals: (.*)$')
RE_REVEALS2 = re.compile('(.*) \- reveals (.*)$')
RE_REVEALS_HAND = re.compile('(.*) \- reveals hand:(.*)$')
RE_BANE = re.compile('(.*) \- reveals bane (.*)$')

RE_TAKES_ACTIONS = re.compile('(.*) \- takes ([0-9]) action(s?)')
RE_TAKES_BUYS = re.compile('(.*) \- takes ([0-9]) buy(s?)')
RE_TAKES_COINS = re.compile('(.*) \- takes ([0-9]) coin(s?)')

# Haven edge case (must be checked before edge case below)
RE_RETURN_SET_ASIDE = re.compile('(.*) \- places set aside (.*) in hand$')
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
RE_DISCARDS_DECK = re.compile('(.*) \- moves deck to discards$')
RE_OVERPAYS = re.compile('(.*) \- overpays for (.*) with (.*) coins?$')
# Some single card cases
RE_WATCHTOWER_TRASH = re.compile('(.*) \- applied Watchtower to trash (.*)$')
RE_WATCHTOWER_TOPDECK = re.compile('(.*) \- applied Watchtower to place (.*) on top of the deck$')
RE_STASH = re.compile('(.*) \- places Stashes at locations: (.*)$')
RE_ROYAL_SEAL = re.compile('(.*) \- applied Royal Seal to place (.*) on top of the deck$')
RE_ROGUE = re.compile('(.*) \- plays Rogue$')
RE_INN = re.compile('(.*) \- gains Inn$')
RE_SCHEME = re.compile('(.*) \- Scheme choice: (.*)$')
RE_FG = re.compile("(.*) \- trashes Fool's Gold$")
RE_BEGGAR = re.compile('(.*) \- reveals reaction Beggar$')
RE_SM_ACTIONS = re.compile('(.*) \- chooses two cards and one action$')
RE_SM_BUY = re.compile('(.*) \- chooses two coins and one buy$')

RE_PLAYS_STR = '(.*) \- plays ([^\(]*)$'
RE_PRINCE_STR = '(.*) \- duration Prince$'
RE_HERMIT_TRASH_STR = '(.*) \- trashes Hermit$'
RE_URCHIN_TRASH_STR = '(.*) \- trashes Urchin$'
RE_MADMAN_GAIN_STR = '(.*) \- gains Madman$'
# think of RE_DEFAULT as something that triggers whenever something interesting happens
RE_DEFAULT_STR = '|'.join([
    RE_PLAYS_STR, RE_PRINCE_STR, RE_HERMIT_TRASH_STR, RE_URCHIN_TRASH_STR,
])

RE_PLAYS = re.compile(RE_PLAYS_STR)
RE_PRINCE = re.compile(RE_PRINCE_STR)
RE_HERMIT_TRASH = re.compile(RE_HERMIT_TRASH_STR)
RE_URCHIN_TRASH = re.compile(RE_URCHIN_TRASH_STR)
RE_MADMAN_GAIN = re.compile(RE_MADMAN_GAIN_STR)
RE_DEFAULT = re.compile(RE_DEFAULT_STR)

# woops forgot one
RE_MERC_GAIN = re.compile('(.*) \- gains Mercenary$')


# play line annotations
TR_ANN = " (Throne Room)"
KC_ANN = " (King's Court)"
HERALD_ANN = " (Herald)"
PROCESSION_ANN = " (Procession)"
COUNTERFEIT_ANN = " (Counterfeit)"
GOLEM_ANN = " (Golem)"
VENTURE_ANN = " (Venture)"
PRINCE_ANN = " (Prince)"
BOM_ANN = " (Band of Misfits)"
HERMIT_ANN = " (trashing for Madman)"
URCHIN_ANN = " (trashing for Mercenary)"
INN_ANN = " (shuffling for Inn)"
ANNOTATIONS = [TR_ANN, KC_ANN, HERALD_ANN, PROCESSION_ANN, COUNTERFEIT_ANN, GOLEM_ANN, VENTURE_ANN, PRINCE_ANN, BOM_ANN, HERMIT_ANN, URCHIN_ANN, INN_ANN]


# helper functions for clean_play_lines, DO NOT CALL ELSEWHERE

def read_until_next_matches(lines, parsed, matcher):
    while lines and matcher.match(lines[0]) is None:
        parsed.append(lines[0])
        lines[:1] = []

def baddecorator(f):
    # very quick fix to check if logic is correct
    # we need to read until the next RE_DEFAULTS line after every return and this is
    # less code than doing it right
    def read_until_resolved_patched(lines):
        parsed = f(lines)
        read_until_next_matches(lines, parsed, RE_DEFAULT)
        return parsed
    return read_until_resolved_patched

@baddecorator
def read_until_resolved(lines):
    """
    lines - passed in list of log lines, modified in place
    curr_matcher - the regex that the first line should satisfy. Raise exception if not true
    next_matcher - the regex that we want to match next
    """
    def remove_annotation(line):
        if line[-1] == ')':
            return line.rsplit(' (',1)[0]
        return line

    # quick sanity check
    # this can happen if the last action played is a giant TR chain, with
    # no other actions in hand to copy
    parsed = []
    m = None
    if not lines:
        return []
    line = lines[0]
    lines[:1] = []
    curr_matcher = RE_DEFAULT
    m = curr_matcher.match(line)
    parsed.append(line)

    # figure out what information to parse
    # Prince case handled here
    if RE_PRINCE.match(parsed[-1]):
        read_until_next_matches(lines, parsed, RE_PLAYS)
        next_play = read_until_resolved(lines)
        if next_play:
            next_play[0] += PRINCE_ANN
        return parsed + next_play
    elif RE_HERMIT_TRASH.match(parsed[-1]):
        if lines and RE_MADMAN_GAIN.match(lines[0]):
            parsed[-1] += HERMIT_ANN
        return parsed
    elif RE_URCHIN_TRASH.match(parsed[-1]):
        if lines and RE_MERC_GAIN.match(lines[0]):
            parsed[-1] += URCHIN_ANN
        return parsed
    else:
        player, card = m.group(1), m.group(2)

    # by this point, the only case is RE_PLAYS

    # TODO handle Herald
    # TODO handle Procession/Counterfeit differently
    # Prince acse is handled above
    if card == "Throne Room":
        read_until_next_matches(lines, parsed, RE_PLAYS)
        first_play = read_until_resolved(lines)
        second_play = read_until_resolved(lines)
        # first verify an action got Throne Roomed
        if not first_play:
            copied = False
        elif not second_play:
            copied = False
        else:
            m = RE_PLAYS.match(first_play[0])
            p1, c1 = m.group(1), m.group(2)
            m2 = RE_PLAYS.match(second_play[0])
            p2, c2 = m.group(1), m.group(2)
            # Yes Python allows these equality chains. It's MAGIC
            copied = (c1 == c2) and (player == p1 == p2) and ('action' in CARDNAME_TO_TYPE[c1])
        if copied:
            second_play[0] += TR_ANN
            return parsed + first_play + second_play
        else:
            # put back other lines to process again
            lines[:0] = first_play + second_play
            return parsed
    elif card == "King's Court":
        read_until_next_matches(lines, parsed, RE_PLAYS)
        first_play = read_until_resolved(lines)
        second_play = read_until_resolved(lines)
        third_play = read_until_resolved(lines)
        if not first_play or not second_play or not third_play:
            copied = False
        else:
            m = RE_PLAYS.match(first_play[0])
            p1, c1 = m.group(1), m.group(2)
            m2 = RE_PLAYS.match(second_play[0])
            p2, c2 = m.group(1), m.group(2)
            m3 = RE_PLAYS.match(third_play[0])
            p3, c3 = m.group(1), m.group(2)
            copied = (c1 == c2 == c3) and (player == p1 == p2 == p3) and ('action' in CARDNAME_TO_TYPE[c1])
        if copied:
            second_play[0] += KC_ANN
            third_play[0] += KC_ANN
            return parsed + first_play + second_play + third_play
        else:
            lines[:0] = [remove_annotation(line) for line in first_play + second_play + third_play]
            return parsed
    elif card == "Procession":
        pass
        """
        read_until_next_matches(parsed, RE_PLAYS)
        first_play = read_until_resolved(lines)
        second_play = read_until_resolved(lines)
        if not firstplay or not second_play:
            copied = False
        else:
            m = RE_PLAYS.match(first_play[0])
            p1, c1 = m.group(1), m.group(2)
            m2 = RE_PLAYS.match(second_play[0])
            p2, c2 = m.group(1), m.group(2)
            copied = (c1 == c2) and (player == p1 == p2) and ('action' in CARDNAME_TO_TYPE[c1])
        if not copied:
            lines[:0] = first_play + second_play
            return parse
        # we still need to check that the card is trashed before fully commiting
        action_card = RE_PLAYS.match(first_play[0]).group(2)
        trash_lines = []
        while lines:
            trash_lines.append(lines[0])
            lines[:1] = []
            if RE_REVEALS.match(trash_lines[-1]):
                continue
            if RE_DEFAULT.match(trash_lines[-1]):
                # must abort
                # TODO how do we know to not process the trash lines in second play call?
                continue
            if RE_TRASHES.match(trash_lines[-1]).group(2) == action_card:
                break

        if not firstplay or not second_play:
            copied = False
        else:
            m = RE_PLAYS.match(first_play[0])
            p1, c1 = m.group(1), m.group(2)
            m2 = RE_PLAYS.match(second_play[0])
            p2, c2 = m.group(1), m.group(2)
        return parsed + first_play + second_play + trashed
        """
    elif card == "Counterfeit":
        pass
    elif card == "Herald":
        # the next line can sometimes not be a Herald reveal, if there are no cards left in the deck
        if lines and RE_REVEALS.match(lines[0]) and 'action' in CARDNAME_TO_TYPE[RE_REVEALS.match(lines[0]).group(2)].split("-"):
            read_until_next_matches(lines, parsed, RE_PLAYS)
            next_play = read_until_resolved(lines)
            if next_play:
                next_play[0] += HERALD_ANN
            return parsed + next_play
        else:
            return parsed
    elif card == "Golem":
        # both plays are from the revealed cards, so ignore the first line of both
        read_until_next_matches(lines, parsed, RE_PLAYS)
        # verify we found an action, treat normally if not
        first_play = read_until_resolved(lines)
        if first_play:
            card = RE_PLAYS.match(first_play[0]).group(2)
            if card in CARDNAME_TO_TYPE and 'action' in CARDNAME_TO_TYPE[card]:
                first_play[0] += GOLEM_ANN
        second_play = read_until_resolved(lines)
        if second_play:
            card = RE_PLAYS.match(second_play[0]).group(2)
            if card in CARDNAME_TO_TYPE and 'action' in CARDNAME_TO_TYPE[card]:
                second_play[0] += GOLEM_ANN
        return parsed + first_play + second_play
    elif card == "Venture":
        # TODO account for when Venture doesn't find a treasure
        # the next played card comes from revealed cards and is ignorable
        read_until_next_matches(lines, parsed, RE_PLAYS)
        next_play = read_until_resolved(lines)
        if next_play:
            m = RE_PLAYS.match(next_play[0])
            if player == m.group(1):
                next_play[0] += VENTURE_ANN
        return parsed + next_play
    elif card == "Prince":
        m = RE_SETS_ASIDE.match(lines[0])
        if m and m.group(2) == "Prince":
            # this is the Prince setting itself aside
            # TODO for now, adding this only makes it ignored, does nothing else
            lines[0] += PRINCE_ANN
        return parsed
    elif card == "Band of Misfits":
        # this acts weird if BoM has no target
        # hopefully that's pretty rare...
        if lines and RE_PLAYS.match(lines[0]):
            next_play = read_until_resolved(lines)
            if next_play:
                next_play[0] += BOM_ANN
            parsed += next_play
        return parsed
    else:
        return parsed

def clean_play_lines(log_lines):
    # return the log with all "plays X" lines annotated
    # This lets us figure out what "plays X" lines need to move cards from the hand and which don't
    # to do this, we first create a list of all lines that are of the form "X plays Y"
    # this gets passed to the helper function which annotates which lines to keep
    # then, go back to the original log and apply these annotations
    # ideally, the method would operaate on the original log, instead of needing
    # a sanitized version. Implement that if this becomes a bottleneck?

    def want_line(line):
        # Hermit trash regex will be redundant once counterfeit and proessino working
        return RE_PLAYS.match(line) or \
            RE_REVEALS.match(line) or \
            RE_PRINCE.match(line) or \
            RE_SETS_ASIDE.match(line) or \
            RE_MADMAN_GAIN.match(line) or \
            RE_HERMIT_TRASH.match(line) or \
            RE_URCHIN_TRASH.match(line) or \
            RE_MERC_GAIN.match(line)
            #RE_TRASHES.match(line) or \

    all_play_lines = [line for line in log_lines if want_line(line)]
    annotated = []
    while all_play_lines:
        # read_until_resolved returns a new list with annotations
        annotated.extend(read_until_resolved(all_play_lines))
    cleaned = []
    for line in log_lines:
        if not want_line(line):
            cleaned.append(line)
        else:
            cleaned.append(annotated[0])
            annotated[:1] = []
    return cleaned

def get_cards_drawn(line):
    line = line[line.rfind('- draws ') + 8:]
    return [card.strip() for card in line.split(', ')]

def get_cards_trashed(line):
    line = line[line.rfind('- trashes ') + 10:]
    return [card.strip() for card in line.split(', ')]

# TODO
# if there are fewer than 5 cards in opening hand, it's off by one
def annotate_cleanup_hands(log_lines):
    # Okay so dealing with this is just so annoying
    # the only way to differentiate hands drawn during cleanup is by where they are
    # in the log, and there may be extraneous shuffle messages in the way too
    # So to avoid dealing with that nonsense, preprocess all of it here
    # This means we do another pass over the entire log text but that
    # should be negligible compared to network times
    # If you want to try to fit this into the other code, feel free...

    # a list of the hands the next player draws during cleanup
    # should handle Outpost, may not handle Possession
    cleanup_start_indices = []
    turn_line_indices = [i for i, line in enumerate(log_lines) if RE_TURNX.match(line)]
    # skip the very first turn line (this is handled in the starting hands section
    for ind in turn_line_indices[1:]:
        cards = []
        # we only expect to see draws or shuffles
        start = ind - 1
        player = None
        while True:
            line = log_lines[start]
            m = RE_DRAWS.match(line)
            if m:
                pname = m.group(1)
                if player is None:
                    player = pname
                elif player != pname:
                    break
                if len(cards) + len(get_cards_drawn(line)) > 5:
                    break
                cards.extend(get_cards_drawn(line))
            elif RE_SHUFFLES.match(line):
                pass
            elif RE_STASH.match(line):
                pass
            else:
                break
            start -= 1
        start += 1
        cleanup_start_indices.append( (player, start) )
    # very very bad patch to fix an edge case
    # basically, we want to make sure that players discard their hand if they trigger a reshuffle
    # on the very last hand drawn before a game over...while making sure it only happens if
    # the opponent didn't resign early
    # this is a first-order apprxoimation of that
    game_over_index = [i for i, line in enumerate(log_lines) if RE_GAMEOVER.match(line)][0]
    # if prev 2 lines are shuffles, draw
    m = RE_SHUFFLES.match(log_lines[game_over_index - 2])
    if m:
        # then add a discard line before the shuffles
        cleanup_start_indices.append( (m.group(1), game_over_index - 2) )


    cleaned = []
    curr = 0
    for pname, start in cleanup_start_indices:
        cleaned.extend(log_lines[curr:start])
        cleaned.append("DISCARD FOR CLEANUP %s" % pname)
        curr = start
    # get remaining lines
    cleaned.extend(log_lines[curr:])
    return cleaned

def annotate_reveals(log_lines):
    # if a card needs to reshuffle before revealing cards, the shuffle line is
    # places before the list of all revealed cards
    cleaned = []
    lookout = False
    for line, next_line in zip(log_lines, log_lines[1:]):
        if lookout:
            lookout = False
            cleaned.append(line + " (shuffle for reveal)")
            continue
        m = RE_SHUFFLES.match(line)
        m2 = RE_LOOKS_AT.match(next_line) or RE_REVEALS.match(next_line) or RE_REVEALS2.match(next_line)
        if m and m2 and not RE_REVEALS_HAND.match(next_line):
            cleaned.append(line + " (shuffle for reveal)")
        else:
            cleaned.append(line)

        # Yes, let's make Lookout not log the reveal. I'm sure it'll be fine -_-
        m = re.search('.* - plays Lookout$', line)
        if m and RE_SHUFFLES.match(next_line):
            lookout = True
    return cleaned

def annotate_rogue(log_lines):
    cleaned = log_lines[:3]
    for line, line2, line3, line4 in zip(log_lines, log_lines[1:], log_lines[2:], log_lines[3:]):
        if RE_ROGUE.match(line):
            m2 = RE_REVEALS.match(line2)
            m3 = RE_TRASHES.match(line3)
            if m2 and not m3:
                # add a discard line
                cleaned.append("%s - discards: %s" % (m2.group(1), m2.group(2)) )
            m2 = RE_SHUFFLES.match(line2)
            m3 = RE_REVEALS.match(line3)
            m4 = RE_TRASHES.match(line4)
            if m2 and m3 and not m4:
                cleaned.append("%s - discards: %s" % (m3.group(1), m3.group(2)) )
        cleaned.append(line4)
    return cleaned

def annotate_envoy(log_lines):
    # we need to remove the second discard line after Envoy is played
    # (the card to discard is logged twice for some reason)
    cleaned = []
    discards = 0
    envoy = False
    for line in log_lines:
        m = RE_PLAYS.match(line)
        if m and m.group(2) == 'Envoy':
            envoy = True
            discards = 2
        elif m:
            envoy = False
            discards = 0

        if RE_DISCARDS.match(line) and envoy:
            if discards == 1:
                discards == 0
                continue
            discards = max(0, discards - 1)
        cleaned.append(line)
    return cleaned

def annotate_inn(log_lines):
    cleaned = log_lines[:2]
    for line, line2, line3 in zip(log_lines, log_lines[1:], log_lines[2:]):
        if RE_INN.match(line):
            if RE_TOPDECKS.match(line2) or RE_TOPDECKS_MULTIPLE.match(line2):
                if RE_SHUFFLES.match(line3):
                    line3 += INN_ANN
        cleaned.append(line3)
    return cleaned

def annotate_fg_reaction(log_lines):
    cleaned = log_lines[:1]
    for line, line2 in zip(log_lines, log_lines[1:]):
        m = RE_FG.match(line)
        m2 = RE_GAINS.match(line2)
        if m and m2 and m.group(1) == m2.group(1) and m2.group(2) == 'Gold':
            line2 += " to top of deck"
        cleaned.append(line2)
    return cleaned

# need to disambiguate one of the gains
def annotate_beggar_reaction(log_lines):
    cleaned = []
    beggar = False
    for line in log_lines:
        if RE_BEGGAR.match(line):
            beggar = True
        elif beggar and re.search('.* - gains Silver$', line):
            line += " to top of deck"
            beggar = False
        cleaned.append(line)
    return cleaned

def annotate_graverobber(log_lines):
    cleaned = log_lines[:1]
    for line, line2 in zip(log_lines, log_lines[1:]):
        if re.search('.* - plays Graverobber', line):
            if RE_GAINS.match(line2):
                line2 += " to top of deck"
        cleaned.append(line2)
    return cleaned

def annotate_library(log_lines):
    cleaned = []
    library = False
    library_lines = []
    for line in log_lines:
        if re.search('.* - plays Library', line):
            library = True
            cleaned.append(line)
        elif RE_PLAYS.match(line) or RE_GAINS.match(line) or RE_BUYS.match(line):
            library = False
            # the discards lines logged are
            # 1. Single line for each card set aside
            # 2. An aggregate line for all discards
            # We need to change the discard logging to a set aside logging
            if library_lines:
                for li_line in library_lines[:-1]:
                    if RE_DISCARDS.match(li_line):
                        li_line = li_line.replace("discards", "sets aside")
                    cleaned.append(li_line)
                # don't transform the last line (if there's only one card it's in
                # the single discard formtat)
                cleaned.append(library_lines[-1])

            cleaned.append(line)
            library_lines = []
        elif library:
            library_lines.append(line)
        else:
            cleaned.append(line)
    return cleaned

def annotate_knights(log_lines):
    cleaned = []
    resolving_card = None
    played_by = None
    has_revealed = False
    for line in log_lines:
        m = RE_PLAYS.match(line)
        if m:
            card = m.group(2)
            if card in KNIGHTS:
                played_by = m.group(1)
                resolving_card = card
                has_revealed = False
            else:
                resolving_card = None
        if RE_REVEALS.match(line):
            has_revealed = True
        if resolving_card is not None and not has_revealed:
            if RE_DISCARDS.match(line) or RE_TRASHES.match(line):
                line += " from hand"
        m = RE_TRASHES.match(line)
        if resolving_card is not None and has_revealed and m:
            if m.group(1) == played_by and m.group(2) == resolving_card:
                line += "from play"
        cleaned.append(line)
    return cleaned




"""
Moves a card from one Counter object to another
"""
# TODO wild cards
def _move(card, fro, to):
    if card not in fro:
        if GameState.WILD in fro:
            # replace the wild with the desired card and rerun
            fro[GameState.WILD] -= 1
            if fro[GameState.WILD] == 0:
                del fro[GameState.WILD]
            fro[card] += 1
            return _move(card, fro, to)
        raise ValueError("Could not move card %s because it was not in fro" % card)
    to[card] += 1
    fro[card] -= 1
    if fro[card] == 0:
        del fro[card]


class PlayerState:
    # store data that is specific to a given player
    def __init__(self):
        self.hand = Counter()
        self.drawpile = Counter()
        self.discarded = Counter()
        self.revealed = Counter()
        self.playarea = Counter()
        self.setaside = Counter()
        self.durationarea = Counter()
        self.trashed = Counter()
        self.actions = 0
        self.actions_played_this_turn = 0
        self.buys = 0
        self.coins = 0
        self.vp_tokens = 0
        self.coin_tokens = 0

    def draw(self, card):
        _move(card, self.drawpile, self.hand)

    def draw_revealed(self, card):
        _move(card, self.revealed, self.hand)

    def draw_all_revealed(self):
        self.hand += self.revealed
        self.revealed = Counter()

    def draw_discarded(self, card):
        _move(card, self.discarded, self.hand)

    def discard(self, card):
        _move(card, self.hand, self.discarded)

    def discard_from_draw(self, card):
        _move(card, self.drawpile, self.discarded)

    def discard_from_play(self, card):
        _move(card, self.playarea, self.discarded)

    def discard_from_set_aside(self, card):
        _move(card, self.setaside, self.discarded)

    def topdeck(self, card):
        _move(card, self.hand, self.drawpile)

    def topdeck_revealed(self, card):
        _move(card, self.revealed, self.drawpile)

    def topdeck_played(self, card):
        _move(card, self.playarea, self.drawpile)

    def topdeck_discarded(self, card):
        _move(card, self.discarded, self.drawpile)

    def discard_hand(self):
        self.discarded += self.hand
        self.hand = Counter()

    def discard_play(self):
        self.discarded += self.playarea
        self.playarea = Counter()

    def discard_draw(self):
        self.discarded += self.drawpile
        self.drawpile = Counter()

    def update_durations(self):
        self.playarea += self.durationarea
        self.durationarea = Counter()

    # TODO fix deck tracking with wild cards
    def shuffle(self):
        assert sum(self.drawpile.values()) == 0, "Tried to trigger shuffle while deck was not empty"
        # TODO FIX THIS
        if GameState.WILD in self.drawpile:
            self.drawpile = Counter()
        self.drawpile += self.discarded
        self.discarded = Counter()

    def shuffle_for_reveal(self):
        # no check on draw pile's size
        # this also doesn't figure out what the wild cards were
        # hopefully, a regular reshuffle happens to resolve it...
        self.drawpile += self.discarded
        self.discarded = Counter()

    def reveal(self, card):
        _move(card, self.drawpile, self.revealed)

    def discard_revealed(self, card):
        _move(card, self.revealed, self.discarded)

    # called on standard gain
    def add_card_to_discard(self, card):
        self.discarded[card] += 1

    def add_card_to_draw(self, card):
        self.drawpile[card] += 1

    def add_card_to_hand(self, card):
        self.hand[card] += 1

    # all lose_card methods bring cards to the trashed zone
    # we never refer to this zone or return it
    def lose_card(self, card):
        _move(card, self.hand, self.trashed)

    def lose_card_from_play(self, card):
        _move(card, self.playarea, self.trashed)

    def lose_card_from_discard(self, card):
        _move(card, self.discarded, self.trashed)

    def lose_card_from_draw(self, card):
        _move(card, self.drawpile, self.trashed)

    def lose_card_from_revealed(self, card):
        _move(card, self.revealed, self.trashed)

    def play(self, card):
        if 'duration' in CARDNAME_TO_TYPE[card]:
            # Goes to play area if tact is only card in hand
            if card == 'Tactician' and sum(self.hand.values()) == 1:
                _move(card, self.hand, self.playarea)
            else:
                _move(card, self.hand, self.durationarea)
        else:
            _move(card, self.hand, self.playarea)

    def play_from_revealed(self, card):
        if 'duration' in CARDNAME_TO_TYPE[card]:
            _move(card, self.revealed, self.durationarea)
        else:
            _move(card, self.revealed, self.playarea)

    def to_dict(self):
        d = dict()
        d['hand'] = dict(self.hand)
        d['draw'] = dict(self.drawpile)
        d['discard'] = dict(self.discarded)
        d['reveal'] = dict(self.revealed)
        d['play'] = dict(self.playarea)
        d['setaside'] = dict(self.setaside)
        d['duration'] = dict(self.durationarea)
        d['actions'] = self.actions
        d['buys'] = self.buys
        d['coins'] = self.coins
        d['coin_tokens'] = self.coin_tokens
        d['vp_tokens'] = self.vp_tokens
        return d

    def set_aside(self, card):
        _move(card, self.hand, self.setaside)

    def set_aside_from_draw(self, card):
        _move(card, self.drawpile, self.setaside)

    def return_set_aside(self, card):
        _move(card, self.setaside, self.hand)

    def draw_wild(self):
        self.hand[GameState.WILD] += 1
        # we need to make sure the number of cards in the deck is correct
        self.drawpile[GameState.WILD] -= 1

    def reset_fields_for_new_turn(self):
        self.actions = 1
        self.buys = 1
        self.coins = 0
        self.actions_played_this_turn = 0



class GameState:
    # holds all the needed data and some extra methods
    WILD = "WILDCARD"

    def __init__(self, pCount, playerInd, debug):
        self.playerInd = playerInd
        self.player_states = dict()
        for pname in playerInd:
            self.player_states[pname] = PlayerState()
        self.pCount = pCount
        self.last_card_played = None
        self.played_by = None
        self.last_card_bought = None
        self.bought_by = None
        self.revealed_reaction = None
        self.revealed_by = None
        self.last_card_gained = None
        self.last_overpay = None
        self.debug = debug
        self.phase = 'action'
        self.supply = None
        self.trashpile = Counter()

    def get_player_names_in_order(self):
        pairs = self.playerInd.items()
        pairs.sort(key=lambda it: it[1])
        return [it[0] for it in pairs]

    def player_index(self, pname):
        return self.playerInd[pname]

    def draw_card(self, pname, card):
        self.player_states[pname].draw_card(card)

    def draw_cards(self, pname, cards):
        for card in cards:
            self.draw_card(pname, card)

    # make a note now, fix later
    def add_to_hand(self, pname, card):
        print 'ADD TO HAND IS DEPRECATED.'
        self.player_states[pname].add_card_to_hand(card)

    def draw_wild(self, pname):
        self.draw_card(pname, GameState.WILD)

    def get_cards_in_play(self):
        return [ps.play for ps in self.player_states.values()]

    def draw_cleanup_hand(self, pname, hand):
        ps = self.player_states[pname]
        ps.discard_hand()
        for card in hand:
            ps.draw(card)

    def get_player(self, pname):
        return self.player_states[pname]

    def set_last_card_played(self, pname, card):
        self.last_card_played = card
        self.played_by = pname
        self.last_card_bought = None
        self.bought_by = None
        self.last_card_gained = None
        self.revealed_reaction = None
        self.revealed_by = None
        self.last_overpay = None
        if 'treasure' in CARDNAME_TO_TYPE[card]:
            self.phase = 'buy'
        else:
            self.phase = 'action'

    def set_last_card_bought(self, pname, card):
        self.last_card_played = None
        self.played_by = None
        self.last_card_bought = card
        self.bought_by = pname
        self.last_card_gained = None
        self.revealed_reaction = None
        self.revealed_by = None
        self.last_overpay = None

    def set_last_card_gained(self, pname, card):
        # don't want to reset anything else
        self.last_card_gained = card

    def set_revealed_reaction(self, pname, card):
        # Don't want to set rest to anything else
        self.revealed_reaction = card
        self.revealed_by = pname

    def set_last_overpay(self, card):
        self.last_overpay = card

    def to_dict(self):
        info = dict()
        for pname in self.player_states:
            info[pname] = self.get_player(pname).to_dict()
        info['supply'] = dict(self.supply)
        info['trash'] = dict(self.trashpile)
        return info

    def _update_supply(self, card):
        if card in RUINSES:
            if self.supply['Ruins'] == 0 and self.debug:
                raise ValueError("Could not gain Ruins")
            self.supply['Ruins'] -= 1
        elif card in self.supply:
            if self.supply[card] == 0 and self.debug:
                raise ValueError("Could not gain %s" % card)
            self.supply[card] -= 1

    # below adapted from log prettifier
    def gain_card(self, pname, card):
        self._update_supply(card)
        self.gain_card_from_elsewhere(pname, card)

    def gain_to_top(self, pname, card):
        self._update_supply(card)
        self.get_player(pname).add_card_to_draw(card)

    def gain_to_hand(self, pname, card):
        self._update_supply(card)
        self.get_player(pname).add_card_to_hand(card)

    def gain_card_from_elsewhere(self, pname, card):
        self.get_player(pname).add_card_to_discard(card)

    def return_to_supply(self, pname, card):
        if card in RUINSES:
            self.supply['Ruins'] += 1
        elif card in self.supply:
            self.supply[card] += 1
        self.player_states[pname].lose_card(card)

    def trash(self, pname, card):
        self.trashpile[card] += 1
        self.player_states[pname].lose_card(card)

    def trash_from_play(self, pname, card):
        self.trashpile[card] += 1
        self.player_states[pname].lose_card_from_play(card)

    def trash_from_discard(self, pname, card):
        self.trashpile[card] += 1
        self.player_states[pname].lose_card_from_discard(card)

    def trash_from_draw(self, pname, card):
        self.trashpile[card] += 1
        self.player_states[pname].lose_card_from_draw(card)

    def trash_from_revealed(self, pname, card):
        self.trashpile[card] += 1
        self.player_states[pname].lose_card_from_revealed(card)


def handle_on_play(player, card):
    if 'action' in CARDNAME_TO_TYPE[card].split('-'):
        player.actions_played_this_turn += 1
    if card in CARDNAME_TO_ACTIONS_BUYS_COINS:
        a, b, c = CARDNAME_TO_ACTIONS_BUYS_COINS[card]
        player.actions += a
        player.buys += b
        player.coins += c
    if card in CARDNAME_TO_COIN_TOKENS:
        player.coin_tokens += CARDNAME_TO_COIN_TOKENS[card]
    if card in CARDNAME_TO_VP_TOKENS:
        player.vp_tokens += CARDNAME_TO_VP_TOKENS[card]

    if card == 'Crossroads' and 'Crossroads' not in player.playarea:
        player.actions += 3
    if card == 'Copper':
        player.coins += player.playarea['Coppersmith']
    if card == 'Conspirator' and player.actions_played_this_turn >= 3:
        player.actions += 1


def snowflakes(line):
    if card == 'Library':
        # if an action is skipped, it logs a discard when it is revealed, and
        # a discard at the end. We need to treat the first as "revealed"
        pass



def generate_game_states(logtext, debug=True):
    # until I'm sure this code works, placing all replay system code
    # at the end in an easy-to-comment-out block

    # copy pasted pre-processing
    # Parse various info from each player's starting cards
    # NOTE: Names are ordered alphabetically, not by order of play
    log_lines = logtext.split("\n")
    supplyl = None
    startcl = []
    turnl = []

    ## PRE-GAME SETUP ###
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
        m = RE_SUPPLY.match(line)
        if m:
            supplyl = m


    for m in startcl:
        pname = m.group(1)

        # Count number of players
        pCount += 1

        # Don't parse games with duplicate bot names
        if pname in pnames:
            raise ParseException('Duplicate name: %s' % (pname))
        else:
            pnames.add(pname)

    # Parse supply
    supply = dict()
    # defaults
    # these counts ignore the starting decks
    for cname in RE_COMMA.split(supplyl.group(1)):
        ## non-supply cards
        if cname in LOOTERS:
            supply['Ruins'] = 10
        if cname in SPOILS_GIVERS:
            supply['Spoils'] = SPECIAL_SUPPLY_COUNTS['Spoils']

        if cname == 'Hermit':
            supply['Madman'] = 10
        elif cname == 'Urchin':
            supply['Mercenary'] = 10
        elif cname == 'Tournament':
            for card in PRIZES:
                supply[card] = 1

        if cname in KNIGHTS:
            cname = 'Knight'
            supply[cname] = 10
        elif cname in SPECIAL_SUPPLY_COUNTS:
            supply[cname] = SPECIAL_SUPPLY_COUNTS[cname]
            if cname == 'Copper':
                supply[cname] -= 7 * pCount
        elif cname == 'Ruins' or cname == 'Curse':
            supply[cname] = 10 * (pCount - 1)
        elif 'victory' in CARDNAME_TO_TYPE[cname]:
            supply[cname] = min(4*pCount, 12)
        else:
            supply[cname] = 10

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

    # create initial state
    state = GameState(pCount, playerInd, debug)
    state.supply = supply
    for m in startcl:
        pname = m.group(1)
        cards = m.group(2)
        for card in cards.split(","):
            card = card.strip()
            # pretend starting cards don't come from the supply
            # this handles shelters case better
            state.gain_card_from_elsewhere(pname, card)
    # do a shuffle to make sure we can draw the cards
    for ps in state.player_states.values():
        ps.shuffle()

    possessed = False
    curr_player = None

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
    # annotations
    # these are preprocessors that make the rest of the parsing easier
    # first do individual cards
    log_lines = annotate_rogue(log_lines)
    log_lines = annotate_envoy(log_lines)
    log_lines = annotate_inn(log_lines)
    log_lines = annotate_library(log_lines)
    log_lines = annotate_fg_reaction(log_lines)
    log_lines = annotate_beggar_reaction(log_lines)
    log_lines = annotate_knights(log_lines)

    # now do cleanup phase
    log_lines = annotate_cleanup_hands(log_lines)

    # clarify cards that don't play from the hand, like Venture or Herald
    log_lines = clean_play_lines(log_lines)

    # do shuffles for reveals correctly
    log_lines = annotate_reveals(log_lines)
    # the returned game_states
    # maps index of log line to game state used
    game_states = []

    # TODO this is the same structure as the above code (continue at the end of every case)
    # Someone this design feels clunky but I can't think of anything better right now?
    for line, next_line in zip(log_lines, log_lines[1:]):
        game_states.append(copy.deepcopy(state))
        """
        for pname in pnames:
            print pname
            print state.get_player(pname).to_dict()
        print line
        """

        m = RE_TURNX.match(line)
        if m:
            possessed = "[possessed]" in line
            curr_player = m.group(1)
            continue
        m = RE_OVERPAYS.match(line)
        if m:
            state.set_last_overpay(m.group(2))
            continue
        m = RE_SHUFFLES.match(line)
        if m:
            pname = m.group(1)
            state.get_player(pname).shuffle()
            continue
        m = RE_SHUFFLES_REVEAL.match(line)
        if m:
            pname = m.group(1)
            state.get_player(pname).shuffle_for_reveal()
            continue
        # in preprocessing, add a special marker for when to trigger cleanup
        if line.startswith("DISCARD FOR CLEANUP"):
            pname = line[len("DISCARD FOR CLEANUP "):]
            state.get_player(pname).discard_hand()
            state.get_player(pname).discard_play()
            state.get_player(pname).update_durations()
            state.get_player(pname).reset_fields_for_new_turn()
            continue
        m = RE_TREASURE_PLAYS.match(line)
        if m:
            pname = m.group(1)
            ps = state.get_player(pname)
            line = line[line.rfind('-'):]
            # Remove "- plays "
            line = line[8:]
            treasure_names_and_num = line.split(', ')
            for token in treasure_names_and_num:
                num, cardname = token.split(' ', 1)
                state.set_last_card_played(pname, cardname)
                num = int(num)
                for _ in xrange(num):
                    handle_on_play(ps, cardname)
                    ps.play(cardname)
                # This doesn't need to update state.last_card_played since
                # the play treasures buttons only plays treasures with no side effects
            continue
        m = RE_PLAYS.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.set_last_card_played(pname, card)
            # Spend an action if its an action card
            if 'action' in CARDNAME_TO_TYPE[card].split('-'):
                state.get_player(pname).actions -= 1
            handle_on_play(state.get_player(pname), card)

            if state.last_card_played in RETURN_TO_SUPPLY_ON_PLAY:
                state.return_to_supply(pname, card)
            elif state.last_card_played == 'Island':
                state.get_player(pname).set_aside(card)
            else:
                state.get_player(pname).play(card)
            continue
        m = RE_ANNOTATED_PLAYS.match(line)
        if m:
            # update the state
            pname = m.group(1)
            card = m.group(2)
            state.set_last_card_played(pname, card)
            handle_on_play(state.get_player(pname), card)
            # sEme casework
            if HERALD_ANN in line or GOLEM_ANN in line or VENTURE_ANN in line:
                # play the card from revealed area
                state.get_player(pname).play_from_revealed(card)
            continue
        m = RE_BUYS.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.set_last_card_bought(pname, card)
            state.phase = 'buy'
            continue
        m = RE_DISCARDS_FROM_HAND.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.get_player(pname).discard(card)
            continue
        m = RE_DISCARDS_DECK.match(line)
        if m:
            pname = m.group(1)
            state.get_player(pname).discard_draw()
            continue
        m = RE_DISCARDS_MULTIPLE.match(line)
        if m:
            pname = m.group(1)
            line = line.rsplit(":", 1)[1]
            cards = [card.strip() for card in line.split(",")]

            if state.last_card_played in DISCARD_FROM_REVEAL:
                for card in cards:
                    state.get_player(pname).discard_revealed(card)
            elif state.last_card_bought in DISCARD_REVEALED_ON_BUY:
                for card in cards:
                    state.get_player(pname).discard_revealed(card)
            elif state.last_card_played in DISCARD_FROM_DRAW:
                for card in cards:
                    state.get_player(pname).discard_from_draw(card)
            elif state.last_card_played in DISCARD_FROM_SET_ASIDE:
                for card in cards:
                    state.get_player(pname).discard_from_set_aside(card)
            else:
                for card in cards:
                    state.get_player(pname).discard(card)
            continue
        m = RE_DISCARDS.match(line)
        if m and state.last_card_played == 'JackOfAllTrades':
            # we need to redraw up to 5 before processing more
            # (next line may be JoaT trash
            pname = m.group(1)
            hand_len = sum(state.get_player(pname).hand.values())
            for _ in range(5-hand_len):
                state.get_player(pname).draw_wild()
            # don't continue, still need to check other cases
        if m and state.last_card_played == 'Vault':
            # check if an opponent is using Vault benefit
            pname = m.group(1)
            if pname != state.played_by:
                # bad hack
                # check if next line is also a discard line for this player
                # this checks for if the player discards 2 cards or not
                # and will only trigger once
                m2 = RE_DISCARDS.match(next_line)
                # the wild is added 1 line early, but that's fine since the other
                # card discarded to opponent's Vault must be in hand and will get handled
                # on the next run through the loop
                if m2 and m2.group(1) == pname:
                    state.get_player(pname).draw_wild()
            # also don't continue

        # no cards discard from the hand on buy or in cleanup
        # for now, assume that in buy phase no discards happen
        # TODO handle this differently for deck tracking implementation
        if m:
            pname = m.group(1)
            card = m.group(2)

            if state.last_overpay == 'Doctor':
                state.get_player(pname).discard_revealed(card)
            elif state.phase == 'buy' and card in ('Treasury', 'Alchemist'):
                state.get_player(pname).discard_from_play(card)
            elif state.last_card_played in DISCARD_FROM_REVEAL:
                # Advisor uses opponent's name
                # TODO Envoy logs 2 discards
                if state.last_card_played in ('Advisor','Envoy'):
                    state.get_player(state.played_by).discard_revealed(card)
                else:
                    state.get_player(pname).discard_revealed(card)
            elif state.last_card_bought in DISCARD_REVEALED_ON_BUY:
                state.get_player(pname).discard_revealed(card)
            elif state.last_card_played in DISCARD_FROM_DRAW:
                state.get_player(pname).discard_from_draw(card)
            elif state.last_card_played in DISCARD_FROM_SET_ASIDE:
                state.get_player(pname).discard_from_set_aside(card)
            else:
                state.get_player(pname).discard(card)

        m = RE_TOPDECKS.match(line)
        # current phase is not very robust so odds are bugs are here
        if m:
            pname = m.group(1)
            card = m.group(2)
            if state.last_card_played == 'JackOfAllTrades':
                # we need to redraw up to 5 before processing more
                # (next line may be JoaT trash
                hand_len = sum(state.get_player(pname).hand.values())
                for _ in range(5-hand_len):
                    state.get_player(pname).draw_wild()
                # don't continue, now check the actual topdeck case
            if state.last_card_played in TOPDECKS_FROM_DRAW:
                # we don't track the order of cards in the draw pile
                # do nothing
                continue

            if state.last_overpay == 'Doctor':
                state.get_player(pname).topdeck_revealed(card)
            elif state.last_card_gained == 'Inn':
                state.get_player(pname).topdeck_discarded(card)
            elif state.last_overpay == 'Herald' or state.last_card_played in TOPDECKS_FROM_DISCARD:
                # topdecks from discard
                state.get_player(pname).topdeck_discarded(card)
            elif state.last_card_played in TOPDECKS_FROM_REVEAL:
                state.get_player(pname).topdeck_revealed(card)
            elif state.last_card_played in TOPDECKS_FROM_PLAY or state.last_card_bought in TOPDECKS_PLAY_ON_BUY:
                state.get_player(pname).topdeck_played(card)
            elif state.phase == 'buy' and 'Herbalist' in state.get_player(pname).playarea and 'treasure' in CARDNAME_TO_TYPE[card]:
                state.get_player(pname).topdeck_played(card)
            elif state.phase == 'buy' and card in TOPDECKS_FROM_PLAY:
                state.get_player(pname).topdeck_played(card)
            elif state.phase == 'action' and state.last_card_gained not in TOPDECKS_ON_GAIN:
                pname = m.group(1)
                card = m.group(2)
                state.get_player(pname).topdeck(card)
            continue
        m = RE_TOPDECKS_MULTIPLE.match(line)
        if m:
            pname = m.group(1)
            cards = m.group(2)
            cards = [card.strip() for card in cards.split(",")]

            if state.last_card_gained == 'Inn':
                for card in cards:
                    state.get_player(pname).topdeck_discarded(card)
            else:
                for card in cards:
                    state.get_player(pname).topdeck_played(card)
            continue
        m = RE_DRAWS.match(line)
        if m:
            pname = m.group(1)
            for card in get_cards_drawn(line):
                state.get_player(pname).draw(card)
            continue
        m = RE_ANNOTATED_TRASH.match(line)
        if m:
            if HERMIT_ANN or URCHIN_ANN in line:
                pname = m.group(1)
                card = m.group(2)
                state.trash_from_play(pname, card)
        m = RE_TRASHES_FROM_HAND.match(line)
        if m:
            pname = m.group(1)
            cards = m.group(2)
            cards = [card.strip() for card in cards.split(",")]
            for card in cards:
                if card != 'Fortress' and not (possessed and pname == curr_player):
                    state.trash(pname, card)
            continue
        m = RE_TRASHES_FROM_PLAY.match(line)
        if m:
            pname = m.group(1)
            cards = m.group(2)
            cards = [card.strip() for card in cards.split(",")]
            for card in cards:
                if card != 'Fortress' and not (possessed and pname == curr_player):
                    state.trash_from_play(pname, card)
                if card == 'Fortress':
                    p = state.get_player(pname)
                    _move('Fortress', p.playarea, p.hand)
            continue
        m = RE_TRASHES.match(line)
        # TODO handle trash edge cases in GameState/PlayerState instead of here
        # That way will probably make it easier to figure out which zone it came from
        if m:
            pname = m.group(1)
            cards = get_cards_trashed(line)
            if state.revealed_reaction == 'Watchtower' and pname == state.revealed_by:
                for card in cards:
                    if card != 'Fortress' and not (possessed and pname == curr_player):
                        state.trash_from_discard(pname, card)
                    if card == 'Fortress':
                        p = state.get_player(pname)
                        _move('Fortress', p.discarded, p.hand)
                # resolved, clear it
                state.revealed_reaction = None
            elif state.last_card_played == 'Hermit':
                # it's impossible to tell whether we trash from the hand or from the discard
                # so, we assume a discard pile trash if we have the choice
                p = state.get_player(pname)
                if not (possessed and pname == curr_player):
                    for card in cards:
                        if card in p.discarded and card == 'Fortress':
                            _move('Fortress', p.discarded, p.hand)
                        elif card in p.discarded and card != 'Fortress':
                            _move(card, p.discarded, p.trashed)
                        elif card != 'Fortress':
                            _move(card, p.hand, p.trashed)
            elif state.last_card_played == 'Death Cart':
                # Assume trash from play if the card trashed is Death Cart
                # There are some edge cases for this but we'll ignore those
                for card in cards:
                    if card == 'Death Cart':
                        state.trash_from_play(pname, card)
                    elif card != 'Fortress':
                        state.trash(pname, card)
            elif state.last_card_bought in TRASHES_PLAY_ON_BUY or state.last_card_played in TRASHES_FROM_PLAY:
                for card in cards:
                    if card != 'Fortress' and not (possessed and pname == curr_player):
                        state.trash_from_play(pname, card)
                    if card == 'Fortress':
                        p = state.get_player(pname)
                        _move('Fortress', p.playarea, p.hand)
            elif state.last_card_played in TRASHES_FROM_DRAW:
                for card in cards:
                    if card != 'Fortress' and not (possessed and pname == curr_player):
                        state.trash_from_draw(pname, card)
                    if card == 'Fortress':
                        p = state.get_player(pname)
                        _move('Fortress', p.drawpile, p.hand)
            elif state.last_card_played in TRASHES_FROM_REVEAL or state.last_overpay == 'Doctor':
                for card in cards:
                    if card != 'Fortress' and not (possessed and pname == curr_player):
                        state.trash_from_revealed(pname, card)
                    if card == 'Fortress':
                        p = state.get_player(pname)
                        _move('Fortress', p.revealed, p.hand)
            else:
                trash_from_hand = state.last_card_bought not in TRASHES_REVEALED_ON_BUY

                if trash_from_hand:
                    # do this case specially
                    if state.last_card_played == 'Treasure Map':
                        if cards == ['Treasure Map', 'Treasure Map']:
                            state.trash(pname, 'Treasure Map')
                            state.trash_from_play(pname, 'Treasure Map')
                    else:
                        for card in cards:
                            if card != 'Fortress' and not (possessed and pname == curr_player):
                                state.trash(pname, card)
                else:
                    # handle on-trash effects
                    for card in cards:
                        # This should only get triggered by Noble Brigand, so below should never run
                        if card == 'Fortress':
                            # not trashed from the hand, so we need to put it back
                            print 'THIS SHOULD NEVER BE PRINTED'
                            state.add_to_hand(pname, 'Fortress')
                        elif card == 'Overgrown Estate':
                            # doesn't log what card is drawn
                            state.get_player(pname).draw_wild()
            continue
        m = RE_RETURN_SET_ASIDE.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.get_player(pname).return_set_aside(card)
            continue
        m = RE_PLACE_MULTIPLE_IN_HAND.match(line)
        if m:
            pname = m.group(1)
            # get cards to put in hand
            line = line.rsplit(":", 1)[-1]
            cards = [card.strip() for card in line.split(",")]
            if state.last_card_played == 'Counting House':
                for card in cards:
                    state.get_player(pname).draw_discarded(card)
            else:
                for card in cards:
                    state.get_player(pname).draw_revealed(card)
            continue
        m = RE_PLACES_IN_HAND.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            if state.last_card_played == 'Counting House':
                state.get_player(pname).draw_discarded(card)
            else:
                state.get_player(pname).draw_revealed(card)
            continue
        m = RE_MOVES_TO_HAND.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.get_player(pname).draw(card)
            continue
        # check before other gains
        m = RE_GAINS_TO_TOP.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.set_last_card_gained(pname, card)
            state.gain_to_top(pname, card)
            continue
        m = RE_GAINS.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.set_last_card_gained(pname, card)
            # only one of last_played or last_bought should be None
            # TODO Tunnel from Sea Hag
            if state.last_card_played in GAINS_CARD_TO_TOP:
                state.gain_to_top(pname, card)
            elif state.last_card_played in GAIN_FROM_ELSEWHERE or state.last_card_bought in GAIN_FROM_ELSEWHERE:
                state.gain_card_from_elsewhere(pname, card)
            elif state.last_card_played in GAIN_TO_HAND:
                state.gain_to_hand(pname, card)
            elif state.last_card_gained in TOPDECKS_ON_GAIN:
                state.gain_to_top(pname, card)
            else:
                state.gain_card(pname, card)
            continue
        m = RE_PASSES.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.get_player(pname).lose_card(card)
            # clean me up later
            next_player_ind = (playerInd[pname] + 1) % pCount
            for p in playerInd:
                if playerInd[p] == next_player_ind:
                    next_player = p
                    state.get_player(next_player).add_card_to_hand(card)
                    break
            continue
        m = RE_RETURN_TO_SUPPLY.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.return_to_supply(pname, card)
            continue
        m = RE_SETS_ASIDE.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            if state.last_card_played in SETS_ASIDE_FROM_DECK:
                state.get_player(pname).set_aside_from_draw(card)
            else:
                state.get_player(pname).set_aside(card)
            continue
        m = RE_NATIVE_VILLAGE_PULL.match(line)
        if m:
            pname = m.group(1)
            line = line.rsplit(":", 1)[1]
            cards = [card.strip() for card in line.split(",")]
            for card in cards:
                state.add_to_hand(pname, card)
        m = RE_LOOKS_AT.match(line)
        if m:
            pname = m.group(1)
            cards = m.group(2)
            cards = [card.strip() for card in cards.split(",")]
            for card in cards:
                state.get_player(pname).reveal(card)
            continue
        # This must be checked before any other reveal parsing code
        m = RE_REACTION.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.set_revealed_reaction(pname, card)
            if card == 'Horse Traders':
                state.get_player(pname).set_aside(card)
            continue
        m = RE_REVEALS_HAND.match(line)
        if m:
            continue
        # also must be checked before the rest of reveal code`
        m = RE_BANE.match(line)
        if m:
            continue
        m = RE_REVEALS.match(line)
        if m:
            if state.last_card_played in REVEALS_FROM_HAND:
                continue
            pname = m.group(1)
            line = line.rsplit(":", 1)[1]
            cards = [card.strip() for card in line.split(",")]
            for card in cards:
                state.get_player(pname).reveal(card)

            if state.last_card_played == 'Apothecary':
                # Apothecary Copper pulling is not listed in the log
                for card in cards:
                    if card == "Copper" or card == "Potion":
                        state.get_player(pname).draw_revealed(card)
            continue

        m = RE_REVEALS2.match(line)
        if m:
            if state.last_card_played in REVEALS_FROM_HAND:
                continue
            if state.last_card_played == 'Black Market':
                continue
            pname = m.group(1)
            line = line[line.index("- reveals")+9:]
            cards = [card.strip() for card in line.split(",")]
            for card in cards:
                state.get_player(pname).reveal(card)

            if state.last_card_played == 'Scrying Pool':
                # Neither is Scrying Pool
                if pname != state.played_by:
                    continue
                state.get_player(pname).draw_all_revealed()
            elif state.last_card_played in ('Wishing Well', 'Mystic'):
                # need to manually put it back if next_line is not a match
                if not RE_PLACES_IN_HAND.match(next_line):
                    for card in cards:
                        state.get_player(pname).topdeck_revealed(card)
            elif state.last_card_played == 'Fortune Teller':
                last_card = cards[-1]
                if 'victory' in CARDNAME_TO_TYPE[last_card]:
                    state.get_player(pname).topdeck_revealed(last_card)
            continue
        m = RE_DURATION.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            if card == 'Horse Traders':
                state.get_player(pname).return_set_aside(card)
            continue
        m = RE_WATCHTOWER_TRASH.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.set_revealed_reaction(pname, 'Watchtower')
            continue
        # by this point the card has been gained so we only need to move it
        # This may break if the card is normally gained to another location
        m = RE_WATCHTOWER_TOPDECK.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            # we don't set revealed reaction because we don't need it for further processing
            # if we have it there are some occasional false positives
            state.get_player(pname).topdeck_discarded(card)
            continue
        m = RE_ROYAL_SEAL.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.get_player(pname).topdeck_discarded(card)
            continue
        m = RE_SCHEME.match(line)
        if m:
            pname = m.group(1)
            card = m.group(2)
            state.get_player(pname).topdeck_played(card)
            continue
        m = RE_TAKES_ACTIONS.match(line)
        if m:
            pname = m.group(1)
            state.get_player(pname).actions += int(m.group(2))
            continue
        m = RE_TAKES_BUYS.match(line)
        if m:
            pname = m.group(1)
            state.get_player(pname).buys += int(m.group(2))
            continue
        m = RE_TAKES_COINS.match(line)
        if m:
            pname = m.group(1)
            state.get_player(pname).coins += int(m.group(2))
            continue
        m = RE_SM_ACTIONS.match(line)
        if m:
            pname = m.group(1)
            state.get_player(pname).actions += 1
            continue
        m = RE_SM_BUY.match(line)
        if m:
            pname = m.group(1)
            state.get_player(pname).coins += 2
            state.get_player(pname).buys += 1
        continue

    # states are out of sync for some reason
    # quick fix
    return log_lines, game_states[1:]
