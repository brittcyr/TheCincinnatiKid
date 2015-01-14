from lib.hand_eval import convert_string_to_int
from Global import State
from lib.starting_hands import classify_hole, HoleScorer
from random import random


PLAY_PREFLOP = .3


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

        numLegalActions = int(data.pop(0))

        legal_actions = []
        for _ in range(numLegalActions):
            legal_actions.append(data.pop(0))

        if numLegalActions == 1:
            return legal_actions[0]

        State.timebank = float(data.pop(0))


        if State.check_fold_to_win:
            return try_to_check(legal_actions)



        # These are the variables based on position
        seat = State.seat
        numActivePlayers = numActivePlayers
        firstRound = any([x for x in prev_actions if 'POST' in x])
        i_called = True if prev_actions and 'CALL' in prev_actions[0] else False


        # FIRST TIME AROUND
        #   3 PLAYERS
        #     UTG               1
        #     SMALL             2
        #       RAISED
        #       CALLED
        #     BIG BLIND         3
        #       RAISED
        #       2 RAISED
        #       CALLED
        #   2 PLAYERS
        #     FIRST             4
        #     SECOND            5
        #       RAISED
        #       CALLED
        # SECOND + TIME AROUND
        #   CALLED LAST TIME    6
        #   RAISED LAST TIME    7

        hand_classify = classify_hole(State.hole_cards[0], State.hole_cards[1])
        hand_score = HoleScorer.score_hole(hand_classify, numActivePlayers)



        ############################## Case 1 ##################################
        ########################################################################
        # UTG three handed

        if seat == 1 and numActivePlayers == 3 and firstRound:
            if hand_score > (PLAY_PREFLOP - .2) / State.looseness:
                # Then we are going to CALL / RAISE

                # This is the case where we must call and cannot raise
                raising_action = [x for x in legal_actions if 'RAISE' in x]
                if not raising_action: return try_to_call(legal_actions)

                # Deciding to raise
                if hand_score > .7:
                    # We are raising if we are good enough
                    lo, hi = split_raise(legal_actions)
                    if not lo: return 'FOLD'

                    if hand_score < .85:
                        return 'RAISE:%d' % lo

                    bet_amt = max(min(int(hand_score * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt

                else:
                    return try_to_call(legal_actions)

                return try_to_call(legal_actions)

            else:
                # Normally fold, but randomly raise. This is a big bluff
                if random() < .02:
                    # Randomly raise here
                    lo, hi = split_raise(legal_actions)
                    if not lo: return 'FOLD'

                    bet_amt = max(min(int(random() * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt
                else:
                    return 'FOLD'






        ############################## Case 2 ##################################
        ########################################################################
        # Small Blind three handed
        # TODO: fill in the logic here

        if seat == 2 and numActivePlayers == 3 and firstRound:
            # TODO: Consider if we are facing a raise already
            if hand_score > (PLAY_PREFLOP - .05) / State.looseness:
                # Then we are going to CALL / RAISE

                # This is the case where we must call and cannot raise
                raising_action = [x for x in legal_actions if 'RAISE' in x]
                if len(raising_action) == 0: return try_to_call(legal_actions)

                # Deciding to raise
                if hand_score > .85:
                    # We are raising if we are good enough
                    lo, hi = split_raise(legal_actions)
                    if not lo: return 'FOLD'

                    if hand_score < .95:
                        return 'RAISE:%d' % lo

                    # Otherwise bet a function of the hi and aggressiveness
                    bet_amt = max(min(int(hand_score * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt

                else:
                    return try_to_call(legal_actions)

                return try_to_call(legal_actions)

            else:
                # Normally fold, but randomly raise
                if random() * hand_score > .15:
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
        # TODO: fill in the logic here
        if seat == 3 and numActivePlayers == 3 and firstRound:
            if hand_score > (PLAY_PREFLOP - .2) / State.looseness:
                # Then we are going to CALL / RAISE

                # This is the case where we must call and cannot raise
                raising_action = [x for x in legal_actions if 'RAISE' in x]
                if len(raising_action) == 0: return try_to_call(legal_actions)

                lo, hi = split_raise(legal_actions)
                if not lo: return try_to_call(legal_actions)

                # Deciding to raise if hand is great
                if hand_score > .95:
                    bet_amt = max(min(int(hand_score * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt

                # If hand is good and no previous raises
                if hand_score > .85 and not any([x for x in prev_actions if 'RAISE' in x]):

                    # Not great, so min raise
                    if hand_score < .9:
                        return 'RAISE:%d' % lo

                    # Otherwise a bigger raise
                    bet_amt = max(min(int(random() * hand_score * \
                            hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt

                return try_to_call(legal_actions)

            else:
                # Normally check/fold, but randomly raise when we cannot check
                if random() < .1 and not can_check(legal_actions):
                    # Randomly raise here
                    lo, hi = split_raise(legal_actions)
                    if not lo: return try_to_check(legal_actions)
                    return 'RAISE:%d' % lo
                else:
                    return try_to_check(legal_actions)







        ############################## Case 4 ##################################
        ########################################################################
        # Not big blind two players
        if numActivePlayers == 2 and firstRound and \
                ((State.num_active == 2 and seat == 1) or
                (State.num_active == 3 and seat == 2)):
            if hand_score > (PLAY_PREFLOP - .2) / State.looseness:
                # Then we are going to CALL / RAISE

                # This is the case where we must call and cannot raise
                raising_action = [x for x in legal_actions if 'RAISE' in x]
                if not raising_action: return try_to_call(legal_actions)

                # Deciding to raise
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
        # TODO: fill in the logic here
        if numActivePlayers == 2 and firstRound and \
                ((State.num_active == 2 and seat == 2) or
                (State.num_active == 3 and seat == 3)):
            # TODO: Consider if we are facing a raise already
            if hand_score > PLAY_PREFLOP / State.looseness:
                # Then we are going to CALL / RAISE

                # This is the case where we must call and cannot raise
                raising_action = [x for x in legal_actions if 'RAISE' in x]
                if len(raising_action) == 0: return try_to_call(legal_actions)

                # Deciding to raise
                if hand_score > .7:
                    # We are raising if we are good enough
                    lo, hi = split_raise(legal_actions)
                    if not lo: return 'FOLD'

                    if hand_score < .75:
                        return 'RAISE:%d' % lo

                    bet_amt = max(min(int(hand_score * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt


                else:
                    return try_to_call(legal_actions)

                return try_to_call(legal_actions)

            else:
                # Normally check/fold, but randomly raise
                if random() * hand_score > PLAY_PREFLOP / State.looseness * .8:
                    # Randomly raise here
                    lo, hi = split_raise(legal_actions)
                    if not lo: return 'CHECK'

                    bet_amt = max(min(int(random() * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt
                else:
                    checking_action = [x for x in legal_actions if 'CHECK' in x]
                    if checking_action:
                        return 'CHECK'
                    return 'FOLD'





        ############################## Case 6 ##################################
        ########################################################################
        # Second round and we called last time
        # TODO: Logic
        if not firstRound and i_called:
            # Play the pot odds
            call_action = [x for x in legal_actions if 'CALL' in x]
            if not call_action: return 'CHECK'
            call_action = call_action[0]

            call_amt = int(call_action.split(':')[-1])
            pot_odds = float(call_amt) / (2 * call_amt + potSize)

            # If we only called and do not have a great hand, reduce our odds
            if numActivePlayers == 3: hand_score = hand_score * hand_score

            if pot_odds < hand_score:
                return call_action
            else:
                return 'FOLD'





        ############################## Case 7 ##################################
        ########################################################################
        # Second round and we raised last time
        # TODO: Logic
        if not firstRound and not i_called:
            # Play the pot odds
            call_action = [x for x in legal_actions if 'CALL' in x]
            if not call_action: return 'CHECK'
            call_action = call_action[0]

            call_amt = int(call_action.split(':')[-1])
            pot_odds = float(call_amt) / (2 * call_amt + potSize)

            # If we only called and do not have a great hand, reduce our odds
            if numActivePlayers == 3: hand_score = hand_score * hand_score

            if pot_odds < hand_score:
                return try_to_call(legal_actions)
            else:
                return 'FOLD'


        # Fall through that should not be used
        return 'CHECK'
