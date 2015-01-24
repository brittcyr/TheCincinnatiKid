from lib.hand_eval import convert_string_to_int
from Global import State
from lib.starting_hands import classify_hole, HoleScorer
from random import random

SEAT1 = 1
SEAT2 = 2
SEAT3 = 3
TWO_PLAYERS = 2
THREE_PLAYERS = 3

PLAY_PREFLOP = .3

UTG_EXTRA = .1
RAISE_UTG = .7
MIN_RAISE_UTG = .85
UTG_BLUFF = .02

SB_EXTRA = .0
SB_RAISE = .6
SB_MAX_RAISE = .95

BB_EXTRA = .1
BB_RAISE = .7
BB_BIG_BET = .85
BB_MAX_RAISE_3H = .95
BB_RAISE_3H = .85
BB_RANDOM_BET = .02

def try_to_check(legal_actions):
    check_action = [x for x in legal_actions if 'CHECK' in x]
    if not check_action:
        return 'FOLD'
    return check_action[0]

def try_to_call(legal_actions):
    call_action = [x for x in legal_actions if 'CALL' in x]
    if not call_action:
        return try_to_check(legal_actions)
    return call_action[0]

def can_check(legal_actions):
    checking_action = [x for x in legal_actions if 'CHECK' in x]
    if checking_action:
        return True
    else:
        return False

def split_raise(legal_actions):
    raising_action = [x for x in legal_actions if 'RAISE' in x]
    if not raising_action:
        return False, False
    r, lo, hi = raising_action[0].split(':')
    lo = int(lo)
    hi = int(hi)
    return lo, hi


class Preflop(object):
    @classmethod
    def get_action(cls, data):
        # GETACTION potSize numBoardCards [boardCards] [stackSizes]
        # numActivePlayers [activePlayers] numLastActions [lastActions]
        # numLegalActions [legalActions] timebank
        data = data.split()
        getaction = data.pop(0)
        potSize = int(data.pop(0))
        numBoardCards = int(data.pop(0))

        board_cards = []
        for _ in range(numBoardCards):
            board_cards.append(convert_string_to_int(data.pop(0)))

        stack1 = int(data.pop(0))
        stack2 = int(data.pop(0))
        stack3 = int(data.pop(0))

        numActivePlayers = int(data.pop(0))
        active1 = data.pop(0)
        active2 = data.pop(0)
        active3 = data.pop(0)

        numLastActions = int(data.pop(0))

        prev_actions = []
        for _ in range(numLastActions):
            prev_actions.append(data.pop(0))
        State.hand_actions += prev_actions

        numLegalActions = int(data.pop(0))

        legal_actions = []
        for _ in range(numLegalActions):
            legal_actions.append(data.pop(0))
        State.timebank = float(data.pop(0))

        if numLegalActions == 1: return legal_actions[0]
        if State.check_fold_to_win: return try_to_check(legal_actions)


        # These are the variables based on position
        seat = State.seat
        firstRound = any([x for x in prev_actions if 'POST' in x])
        i_called = True if prev_actions and 'CALL' in prev_actions[0] else False


        # FIRST TIME AROUND
        #   3 PLAYERS
        #     UTG               1
        #     SMALL             2
        #     BIG BLIND         3
        #   2 PLAYERS
        #     FIRST             4
        #     SECOND            5
        # SECOND TIME AROUND
        #   CALLED LAST TIME    6
        #   RAISED LAST TIME    7

        hand_classify = classify_hole(State.hole_cards[0], State.hole_cards[1])
        hand_score = HoleScorer.score_hole(hand_classify, numActivePlayers)


        ############################## Case 1 ##################################
        ########################################################################
        # UTG three handed
        if seat == SEAT1 and numActivePlayers == THREE_PLAYERS and firstRound:
            if hand_score > (PLAY_PREFLOP - UTG_EXTRA) / State.looseness:
                # Then we are going to CALL / RAISE

                # This is the case where we must call and cannot raise
                raising_action = [x for x in legal_actions if 'RAISE' in x]
                if not raising_action: return try_to_call(legal_actions)

                # Deciding to raise
                if hand_score > RAISE_UTG:
                    lo, hi = split_raise(legal_actions)
                    if not lo: return 'FOLD'

                    if hand_score < MIN_RAISE_UTG:
                        return 'RAISE:%d' % lo
                    else:
                        bet_amt = max(min(int(hand_score * hi * \
                                State.aggressiveness), hi), lo)
                        return 'RAISE:%d' % bet_amt

                # Call if we don't want to raise
                return try_to_call(legal_actions)
            else:
                # Normally fold, but randomly raise. This is a big bluff
                if random() < UTG_BLUFF:
                    lo, hi = split_raise(legal_actions)
                    if not lo: return 'FOLD'

                    bet_amt = max(min(int(random() * hi * \
                            State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt
                else:
                    return 'FOLD'



        ############################## Case 2 ##################################
        ########################################################################
        # Small Blind three handed
        if seat == SEAT2 and numActivePlayers == THREE_PLAYERS and firstRound:
            # Decrease my score if there is a raise already
            if [x for x in prev_actions if 'RAISE' in x]:
                hand_score = hand_score * hand_score

            if hand_score > (PLAY_PREFLOP - SB_EXTRA) / State.looseness:
                raising_action = [x for x in legal_actions if 'RAISE' in x]
                if not raising_action: return try_to_call(legal_actions)

                # Deciding to raise
                if hand_score > SB_RAISE:
                    lo, hi = split_raise(legal_actions)
                    if not lo: return 'FOLD'

                    if hand_score < SB_MAX_RAISE:
                        return 'RAISE:%d' % lo

                    # Otherwise bet a function of the hi and aggressiveness
                    bet_amt = max(min(int(hand_score * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt

                return try_to_call(legal_actions)
            else:
                # Normally fold, but randomly raise
                if random() * hand_score > PLAY_PREFLOP:
                    # Randomly raise here
                    lo, hi = split_raise(legal_actions)
                    if not lo: return 'FOLD'

                    bet_amt = max(min(int(random() * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt
                else:
                    return 'FOLD'



        ############################## Case 3 ##################################
        ########################################################################
        # Big Blind three handed
        if seat == SEAT3 and numActivePlayers == THREE_PLAYERS and firstRound:
            if hand_score > (PLAY_PREFLOP - BB_EXTRA) / State.looseness:
                lo, hi = split_raise(legal_actions)
                if not lo: return try_to_call(legal_actions)

                # Deciding to raise if hand is great
                if hand_score > BB_MAX_RAISE_3H:
                    return 'RAISE:%d' % hi

                # If hand is good and no previous raises
                if hand_score > BB_RAISE_3H and [x for x in prev_actions if 'RAISE' in x]:
                    # Otherwise a bigger raise
                    bet_amt = max(min(int(random() * hand_score * \
                            hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt

                return try_to_call(legal_actions)

            else:
                # Normally check/fold, but randomly raise when we cannot check
                if random() < BB_RANDOM_BET and not can_check(legal_actions):
                    # Randomly raise here
                    lo, hi = split_raise(legal_actions)
                    if not lo: return try_to_check(legal_actions)
                    return 'RAISE:%d' % lo
                else:
                    return try_to_check(legal_actions)


        ############################## Case 4 ##################################
        ########################################################################
        # Not big blind two players
        if numActivePlayers == TWO_PLAYERS and firstRound and \
                ((State.num_active == TWO_PLAYERS and seat == SEAT1) or
                (State.num_active == THREE_PLAYERS and seat == SEAT2)):
            if hand_score > (PLAY_PREFLOP - .2) / State.looseness:
                raising_action = [x for x in legal_actions if 'RAISE' in x]
                if not raising_action: return try_to_call(legal_actions)

                if hand_score > .7:
                    # We are raising if we are good enough
                    lo, hi = split_raise(legal_actions)
                    if not lo: return 'FOLD'

                    if hand_score < .75:
                        return 'RAISE:%d' % lo

                    bet_amt = max(min(int(hand_score * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt

                return try_to_call(legal_actions)
            else:
                # Normally fold, but randomly raise
                if random() < .1:
                    # Randomly raise here
                    lo, hi = split_raise(legal_actions)
                    if not lo: return 'FOLD'

                    bet_amt = max(min(int(random() * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt
                else:
                    return 'FOLD'



        ############################## Case 5 ##################################
        ########################################################################
        # Big Blind two handed
        if numActivePlayers == TWO_PLAYERS and firstRound and \
                ((State.num_active == TWO_PLAYERS and seat == SEAT2) or
                (State.num_active == THREE_PLAYERS and seat == SEAT3)):
            # Decrease my score if there is a raise already
            if [x for x in prev_actions if 'RAISE' in x]:
                hand_score = hand_score * hand_score

            if hand_score > (PLAY_PREFLOP - BB_EXTRA) / State.looseness:
                # This is the case where we must call and cannot raise
                raising_action = [x for x in legal_actions if 'RAISE' in x]
                if not raising_action: return try_to_call(legal_actions)

                # Deciding to raise
                if hand_score > BB_RAISE:
                    lo, hi = split_raise(legal_actions)
                    if not lo: return try_to_call(legal_actions)

                    if hand_score < BB_BIG_BET: return 'RAISE:%d' % lo

                    bet_amt = max(min(int(hand_score * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt

                return try_to_call(legal_actions)
            else:
                # Normally check/fold, but randomly raise
                if random() * hand_score > PLAY_PREFLOP / State.looseness * .8:
                    # Randomly raise here
                    lo, hi = split_raise(legal_actions)
                    if not lo: return try_to_check(legal_actions)

                    bet_amt = max(min(int(random() * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt
                else:
                    return try_to_check(legal_actions)



        ############################## Case 6 ##################################
        ########################################################################
        # Second round and we called last time
        if not firstRound and i_called:
            # Play the pot odds
            call_action = [x for x in legal_actions if 'CALL' in x]
            if not call_action: return 'CHECK'

            call_amt = int(call_action[0].split(':')[-1])
            pot_odds = float(call_amt) / (call_amt + potSize)

            # If we only called and do not have a great hand, reduce our odds
            if numActivePlayers == THREE_PLAYERS: hand_score = hand_score ** 2

            prev_bets = [x for x in prev_actions if 'RAISE' in x or 'BET' in x]
            numBets = len(prev_bets)
            hand_score = hand_score ** numBets

            return call_action[0] if pot_odds < hand_score else 'FOLD'



        ############################## Case 7 ##################################
        ########################################################################
        # Second round and we raised last time
        if not firstRound and not i_called:
            # Play the pot odds
            call_action = [x for x in legal_actions if 'CALL' in x]
            if not call_action: return 'CHECK'

            call_amt = int(call_action[0].split(':')[-1])
            pot_odds = float(call_amt) / (call_amt + potSize)

            # If we only called and do not have a great hand, reduce our odds
            if numActivePlayers == THREE_PLAYERS: hand_score = hand_score ** 2

            prev_bets = [x for x in prev_actions if 'RAISE' in x or 'BET' in x]
            numBets = len(prev_bets)
            hand_score = hand_score ** numBets

            return try_to_call(legal_actions) if pot_odds < hand_score else 'FOLD'

        return 'CHECK'
