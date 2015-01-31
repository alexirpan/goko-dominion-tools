# Dominion game constants.

CORE_CARDS = ['Estate', 'Duchy', 'Province', 'Colony',
              'Copper', 'Silver', 'Gold', 'Platinum',
              'Potion', 'Curse', 'Ruins']

# this stores all cards with more than 10 cards in the supply
# doesn't hold victory cards, those are handled in another case
SPECIAL_SUPPLY_COUNTS = {
    'Copper': 60,
    'Silver': 40,
    'Gold': 30,
    'Platinum': 12,
    'Potion': 12,
    'Spoils': 15,
    'Rats': 20,
}

# NOTE: Spoils can't be handled unambigously
NON_SUPPLY = {'Diadem': 'Tournament', 'Followers': 'Tournament',
              'Trusty Steed': 'Tournament', 'Princess': 'Tournament',
              'Bag of Gold': 'Tournament', 'Madman': 'Hermit',
              'Mercenary': 'Urchin'}

VP_CARDS = ['Estate', 'Duchy', 'Province', 'Colony', 'Gardens', 'Silk Road',
            'Vineyard', 'Fairgrounds', 'Duke', 'Feodum', 'Great Hall',
            'Nobles', 'Tunnel', 'Island']

RUINSES = ['Ruined Library', 'Ruined Village', 'Survivors', 'Abandoned Mine',
           'Ruined Market']

KNIGHTS = ['Dame Anna', 'Dame Josephine', 'Dame Molly', 'Dame Natalie',
           'Dame Sylvia', 'Sir Bailey', 'Sir Destry', 'Sir Vander',
           'Sir Michael', 'Sir Martin']

SHELTERS = ['Hovel', 'Overgrown Estate', 'Necropolis']

LOOTERS = ['Marauder', 'Death Cart', 'Cultist']

SPOILS_GIVERS = ['Marauder', 'Bandit Camp', 'Pillage']

PRIZES = ['Diadem', 'Followers', 'Trusty Steed', 'Princess', 'Bag of Gold']

BOT_NAMES = ['Banker Bot', 'Conqueror Bot', 'Defender Bot', 'Lord Bottington',
             'Serf Bot', 'Villager Bot', 'Warlord Bot', 'Village Idiot Bot']
bot_copies = []
for bot in BOT_NAMES:
    for nth in ['I', 'II', 'III', 'IV', 'V', 'VI']:
        bot_copies.append('%s %s' % (bot, nth))
BOT_NAMES += bot_copies

# A giant card type dictionary
# Wheeeeeee
# (This is copy pasted from the Javascript for the log prettifier,
# thank you for your busywork sacrifice)
CARDNAME_TO_TYPE = {
    'Border Village':'action',
    'Farming Village':'action',
    'Mining Village':'action',
    'Native Village':'action',
    'Walled Village':'action',
    'Worker\'s Village':'action',
    'Ruined Village':'action-ruins',
    'Fishing Village':'action-duration',
    'Village':'action',
    'Ruined Library':'action-ruins',
    'Library':'action',
    'Abandoned Mine':'action-ruins',
    'Mine':'action',
    'Bag of Gold':'action',
    'Fool\'s Gold':'treasure-reaction',
    'Gold':'treasure',
    'Overgrown Estate':'shelter-victory',
    'Estate':'victory',
    'Counting House':'action',
    'Count':'action',
    'Coppersmith':'action',
    'Copper':'treasure',
    'Ruined Market':'action-ruins',
    'Grand Market':'action',
    'Black Market':'action',
    'Market Square':'action-reaction',
    'Market':'action',
    'Adventurer':'action',
    'Alchemist':'action',
    'Altar':'action',
    'Ambassador':'action',
    'Apothecary':'action',
    'Apprentice':'action',
    'Armory':'action',
    'Band of Misfits':'action',
    'Bandit Camp':'action',
    'Baron':'action',
    'Bazaar':'action',
    'Bishop':'action',
    'Bridge':'action',
    'Bureaucrat':'action',
    'Cartographer':'action',
    'Catacombs':'action',
    'Cellar':'action',
    'Chancellor':'action',
    'Chapel':'action',
    'City':'action',
    'Conspirator':'action',
    'Council Room':'action',
    'Courtyard':'action',
    'Crossroads':'action',
    'Cultist':'action',
    'Cutpurse':'action',
    'Dame Anna':'action',
    'Dame Molly':'action',
    'Dame Natalie':'action',
    'Dame Sylvia':'action',
    'Death Cart':'action',
    'Develop':'action',
    'Duchess':'action',
    'Embargo':'action',
    'Embassy':'action',
    'Envoy':'action',
    'Expand':'action',
    'Explorer':'action',
    'Familiar':'action',
    'Feast':'action',
    'Festival':'action',
    'Followers':'action',
    'Forager':'action',
    'Forge':'action',
    'Fortress':'action',
    'Fortune Teller':'action',
    'Ghost Ship':'action',
    'Golem':'action',
    'Goons':'action',
    'Governor':'action',
    'Graverobber':'action',
    'Haggler':'action',
    'Hamlet':'action',
    'Harvest':'action',
    'Herbalist':'action',
    'Hermit':'action',
    'Highway':'action',
    'Hunting Grounds':'action',
    'Hunting Party':'action',
    'Inn':'action',
    'Ironmonger':'action',
    'Ironworks':'action',
    'JackOfAllTrades':'action',
    'Jester':'action',
    'Junk Dealer':'action',
    'King\'s Court':'action',
    'Knights':'action',
    'Laboratory':'action',
    'Lookout':'action',
    'Madman':'action',
    'Mandarin':'action',
    'Marauder':'action',
    'Margrave':'action',
    'Masquerade':'action',
    'Menagerie':'action',
    'Mercenary':'action',
    'Militia':'action',
    'Minion':'action',
    'Mint':'action',
    'Moneylender':'action',
    'Monument':'action',
    'Mountebank':'action',
    'Mystic':'action',
    'Navigator':'action',
    'Noble Brigand':'action',
    'Nomad Camp':'action',
    'Oasis':'action',
    'Oracle':'action',
    'Pawn':'action',
    'Pearl Diver':'action',
    'Peddler':'action',
    'Pillage':'action',
    'Pirate Ship':'action',
    'Poor House':'action',
    'Possession':'action',
    'Prince':'action',
    'Princess':'action',
    'Procession':'action',
    'Rabble':'action',
    'Rats':'action',
    'Rebuild':'action',
    'Remake':'action',
    'Remodel':'action',
    'Rogue':'action',
    'Saboteur':'action',
    'Sage':'action',
    'Salvager':'action',
    'Scavenger':'action',
    'Scheme':'action',
    'Scout':'action',
    'Scrying Pool':'action',
    'Sea Hag':'action',
    'Shanty Town':'action',
    'Sir Bailey':'action',
    'Sir Destry':'action',
    'Sir Martin':'action',
    'Sir Michael':'action',
    'Sir Vander':'action',
    'Smithy':'action',
    'Smugglers':'action',
    'Spice Merchant':'action',
    'Spy':'action',
    'Squire':'action',
    'Stables':'action',
    'Steward':'action',
    'Storeroom':'action',
    'Swindler':'action',
    'Thief':'action',
    'Throne Room':'action',
    'Torturer':'action',
    'Tournament':'action',
    'Trade Route':'action',
    'Trading Post':'action',
    'Transmute':'action',
    'Treasure Map':'action',
    'Treasury':'action',
    'Tribute':'action',
    'Trusty Steed':'action',
    'University':'action',
    'Upgrade':'action',
    'Urchin':'action',
    'Vagrant':'action',
    'Vault':'action',
    'Wandering Minstrel':'action',
    'Warehouse':'action',
    'Wishing Well':'action',
    'Witch':'action',
    'Young Witch':'action',
    'Woodcutter':'action',
    'Workshop':'action',
    'Beggar':'action-reaction',
    'Watchtower':'action-reaction',
    'Horse Traders':'action-reaction',
    'Moat':'action-reaction',
    'Secret Chamber':'action-reaction',
    'Trader':'action-reaction',
    'Bank':'treasure',
    'Cache':'treasure',
    'Contraband':'treasure',
    'Counterfeit':'treasure',
    'Diadem':'treasure',
    'Hoard':'treasure',
    'Horn of Plenty':'treasure',
    'Ill-Gotten Gains':'treasure',
    'Loan':'treasure',
    'Philosopher\'s Stone':'treasure',
    'Platinum':'treasure',
    'Potion':'treasure',
    'Quarry':'treasure',
    'Royal Seal':'treasure',
    'Silver':'treasure',
    'Spoils':'treasure',
    'Stash':'treasure',
    'Talisman':'treasure',
    'Venture':'treasure',
    'Colony':'victory',
    'Duchy':'victory',
    'Duke':'victory',
    'Fairgrounds':'victory',
    'Farmland':'victory',
    'Feodum':'victory',
    'Gardens':'victory',
    'Province':'victory',
    'Silk Road':'victory',
    'Vineyard':'victory',
    'Caravan':'action-duration',
    'Haven':'action-duration',
    'Lighthouse':'action-duration',
    'Merchant Ship':'action-duration',
    'Outpost':'action-duration',
    'Tactician':'action-duration',
    'Wharf':'action-duration',
    'Survivors':'action-ruins',
    'Dame Josephine':'action-victory',
    'Great Hall':'action-victory',
    'Nobles':'action-victory',
    'Island':'action-victory',
    'Harem':'treasure-victory',
    'Hovel':'shelter-reaction',
    'Necropolis':'action-shelter',
    'Tunnel':'victory-reaction',
    'victory point chips':'vp-chip',
    'Curse':'curse',
    'Candlestick Maker':'action',
    'Stonemason':'action',
    'Doctor':'action',
    'Masterpiece':'treasure',
    'Advisor':'action',
    'Herald':'action',
    'Plaza':'action',
    'Taxman':'action-attack',
    'Baker':'action',
    'Butcher':'action',
    'Journeyman':'action',
    'Merchant Guild':'action',
    'Soothsayer':'action-attack',
}

# These help disambiguate actions taken based on the last action played
# TODO IGG gains a copper to hand on play, but gains a curse to discard on buy
# must disambiguate between the two (probably has its own edge case)
# TODO Beggar on play vs reaction
GAIN_TO_HAND = [
    'Mine', 'Trading Post', 'Torturer', 'Explorer', 'Ill-Gotten Gains', 'Beggar',
]

GAIN_TO_TOP = [
    'Bureaucrat', 'Tournament',
]

# these are cards that gain from somewhere not in the supply (usually a trashing attack)
# for these purposes we treat Spoils, Madman, as supply piles
# TODO find out if Graverobber gain is from trash or from supply
GAIN_FROM_ELSEWHERE = [
    'Thief', 'Noble Brigand', 'Rogue', 'Graverobber'
]

# Treasure Map is not in this list because it's an odd edge case
# It's handled explicitly elsewhere
# TODO since extra play lines are removed, these occasionally may act weird
# if they are Throned or Counterfeited, and in particular Procession is broken
# FIX THIS
# TODO handle Hermit
# Hermit trashes from hand, or discard, or from play when no cards are bought
# for now this ignore all of that.
# TODO handle Death Cart
# Death Cart trashes either itself or a card from hand
# need to check between the two
# Fortress is very special and handled back in the parser
# TODO handle Knights
# (both trash from play if Knight revealed, or from revealed cards, or for Dame Anna from hand)
# for now ignore it all
TRASHES_FROM_PLAY = ['Feast', 'Mining Village', 'Horn of Plenty', 'Hermit', 'Urchin', 'Death Cart', 'Procession', 'Counterfeit', 'Pillage', 'Embargo',
    'Dame Anna', 'Dame Josephine', 'Dame Molly', 'Dame Natalie', 'Dame Sylvia',
    'Sir Bailey', 'Sir Destry', 'Sir Martin', 'Sir Michael', 'Sir Vander',
]

TRASHES_FROM_REVEAL = [
    'Thief', 'Swindler', 'Saboteur', 'Noble Brigand', 'Pirate Ship', 'Loan', 'Rebuild', 'Rogue',
    'Dame Anna', 'Dame Josephine', 'Dame Molly', 'Dame Natalie', 'Dame Sylvia',
    'Sir Bailey', 'Sir Destry', 'Sir Martin', 'Sir Michael', 'Sir Vander',
    'Doctor',
]

TRASHES_FROM_DRAW = [
    'Lookout',
]

# TODO handle Sir Michael
DISCARD_FROM_REVEAL = [
    'Library', 'Hunting Party', 'Thief', 'Adventurer', 'Saboteur', 'Tribute', 'Navigator', 'Pirate Ship', 'Noble Brigand', 'Golem', 'Loan', 'Rabble', 'Venture', 'Fortune Teller', 'Farming Village', 'Harvest', 'Oracle', 'Jester', 'JackOfAllTrades', 'Cartographer', 'Sage', 'Ironmonger', 'Wandering Minstrel', 'Catacombs', 'Rebuild', 'Rogue', 'Survivors',
    'Dame Anna', 'Dame Josephine', 'Dame Molly', 'Dame Natalie', 'Dame Sylvia',
    'Sir Bailey', 'Sir Destry', 'Sir Martin', 'Sir Michael', 'Sir Vander',
    'Advisor', 'Journeyman', 'Envoy',
]

# Sometimes the reveal line is not explicitly given, usually when only 1 card is revealed
# (however, not always)
DISCARD_FROM_DRAW = [
    'Spy', 'Scrying Pool', 'Sea Hag', 'Duchess', 'Lookout',
]

TOPDECKS_FROM_REVEAL = [
    'Spy', 'Wishing Well', 'Scout', 'Navigator', 'Apothecary', 'Scrying Pool', 'Rabble', 'Fortune Teller', 'Duchess', 'Oracle', 'Cartographer', 'Scavenger', 'Wandering Minstrel', 'Survivors', 'Doctor', 'Herald', 'Vagrant', 'JackOfAllTrades','Ironmonger', 'Survivors',
]

# TODO all of these cards are triggered in cleanup
# So, they may not be the resolving action anymore
# need to handle this properly
TOPDECKS_FROM_PLAY = ['Treasury', 'Herbalist', 'Alchemist']

# Note - Horse Traders reaction works by luck
# since for every Attack in the game, it is not in the list below,
# so the HT revealed is correctly set aside
# TODO make this robust and explicit
SETS_ASIDE_FROM_DECK = ['Native Village']

# TODO implement Watchtower, Mint on gain, Royal Seal topdeck, Walled Village, reactions...
# In general, do effects that occur when the card is NOT being played
# TODO implement Band of Misfits (oh my god please no)
# TODO implement Black Market

TOPDECKS_ON_BUY = ['Inn']

# Nomad Camp isn't actually needed here, the NC topdeck isn't logged
# just here for completion
TOPDECKS_ON_GAIN = ['Inn', 'Nomad Camp']

# This is a very silly name, but it's helpful to have
TOPDECKS_FROM_DRAW = [
    'Pearl Diver', 'Duchess', 'Spy', 'Scrying Pool', 'Sea Hag', 'Lookout',
]


# Doctor triggers on overpay and is handled separately
# For now TRASHES_REVEALED_ON_BUY does nothing because it's only triggered by NO
TRASHES_REVEALED_ON_BUY = ['Noble Brigand']
DISCARD_REVEALED_ON_BUY = ['Noble Brigand']
TRASHES_PLAY_ON_BUY = ['Mint']

RETURN_TO_SUPPLY_ON_PLAY = ['Spoils', 'Madman']

REVEALS_FROM_HAND = [
    'Ambassador', 'Mint', 'Pillage', 'Shanty Town',
]

# These are cards that need special code to work because they log things in weird ways
# I hate these so much
# May or may not actually use this list
# It's possible the edge cases will be all over the place
SPECIAL_SNOWFLAKES = [
    'Library',
    'Hermit',
    'Sir Michael',
    'Beggar',
    'Graverobber',
    'Apothecary',
    'Scrying Pool',
    'Nomad Camp',
    'Pearl Diver',
    'Death Card',
    'Herald',
    'Doctor',
    'Island',
    'Lookout',
]

