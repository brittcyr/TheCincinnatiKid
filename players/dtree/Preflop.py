from lib.hand_eval import convert_string_to_int
from Global import State
from lib.starting_hands import classify_hole, HoleScorer
from random import random


PLAY_PREFLOP = .5

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
            if 'CHECK' in legal_actions:
                return 'CHECK'
            elif 'FOLD' in legal_actions:
                return 'FOLD'
            else:
                return legal_actions[0]



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
            if hand_score > PLAY_PREFLOP * State.looseness:
                # Then we are going to CALL / RAISE

                # This is the case where we must call and cannot raise
                raising_action = [x for x in legal_actions if 'RAISE' in x]
                if len(raising_action) == 0:
                    call_action = [x for x in legal_actions if 'CALL' in x]
                    if not call_action:
                        return 'CHECK'
                    return call_action[0]

                # Deciding to raise
                if hand_score > .7:
                    # We are raising if we are good enough
                    raising_action = [x for x in legal_actions if 'RAISE' in x][0]
                    r, lo, hi = raising_action.split(':')
                    lo = int(lo)
                    hi = int(hi)

                    if hand_score < .75:
                        return 'RAISE:%d' % lo

                    bet_amt = max(min(int(hand_score * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt


                else:
                    call_action = [x for x in legal_actions if 'CALL' in x]
                    # Should not happen
                    if not call_action:
                        return 'CHECK'
                    return call_action[0]

                call_action = [x for x in legal_actions if 'CALL' in x]
                # Should not happen
                if not call_action:
                    return 'CHECK'
                return call_action[0]

            else:
                # Normally fold, but randomly raise
                if random() < .1:
                    # Randomly raise here
                    raising_action = [x for x in legal_actions if 'RAISE' in x]
                    if not raising_action:
                        return 'FOLD'
                    r, lo, hi = raising_action[0].split(':')
                    lo = int(lo)
                    hi = int(hi)
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
            if hand_score > PLAY_PREFLOP * State.looseness:
                # Then we are going to CALL / RAISE

                # This is the case where we must call and cannot raise
                raising_action = [x for x in legal_actions if 'RAISE' in x]
                if len(raising_action) == 0:
                    call_action = [x for x in legal_actions if 'CALL' in x]
                    if not call_action:
                        return 'CHECK'
                    return call_action[0]

                # Deciding to raise
                if hand_score > .7:
                    # We are raising if we are good enough
                    raising_action = [x for x in legal_actions if 'RAISE' in x][0]
                    r, lo, hi = raising_action.split(':')
                    lo = int(lo)
                    hi = int(hi)

                    if hand_score < .75:
                        return 'RAISE:%d' % lo

                    bet_amt = max(min(int(hand_score * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt


                else:
                    call_action = [x for x in legal_actions if 'CALL' in x]
                    if not call_action:
                        return 'CHECK'
                    return call_action[0]

                call_action = [x for x in legal_actions if 'CALL' in x]
                if not call_action:
                    return 'CHECK'
                return call_action[0]

            else:
                # Normally fold, but randomly raise
                if random() < .1:
                    # Randomly raise here
                    raising_action = [x for x in legal_actions if 'RAISE' in x]
                    if not raising_action:
                        return 'FOLD'
                    r, lo, hi = raising_action[0].split(':')
                    lo = int(lo)
                    hi = int(hi)
                    bet_amt = max(min(int(random() * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt
                else:
                    return 'FOLD'






        ############################## Case 3 ##################################
        ########################################################################
        # Big Blind three handed
        # TODO: fill in the logic here
        if seat == 3 and numActivePlayers == 3 and firstRound:
            # TODO: Consider if we are facing a raise already
            if hand_score > PLAY_PREFLOP * State.looseness:
                # Then we are going to CALL / RAISE

                # This is the case where we must call and cannot raise
                raising_action = [x for x in legal_actions if 'RAISE' in x]
                if len(raising_action) == 0:
                    call_action = [x for x in legal_actions if 'CALL' in x]
                    if not call_action:
                        return 'CHECK'
                    return call_action[0]

                # Deciding to raise
                if hand_score > .9:
                    # We are raising if we are good enough
                    raising_action = [x for x in legal_actions if 'RAISE' in x][0]
                    r, lo, hi = raising_action.split(':')
                    lo = int(lo)
                    hi = int(hi)

                    if hand_score < .95:
                        return 'RAISE:%d' % lo

                    bet_amt = max(min(int(hand_score * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt


                else:
                    call_action = [x for x in legal_actions if 'CALL' in x]
                    if not call_action:
                        return 'CHECK'
                    return call_action[0]

                call_action = [x for x in legal_actions if 'CALL' in x]
                if not call_action:
                    return 'CHECK'
                return call_action[0]

            else:
                # Normally check/fold, but randomly raise
                if random() < .1:
                    # Randomly raise here
                    raising_action = [x for x in legal_actions if 'RAISE' in x]
                    if not raising_action:
                        checking_action = [x for x in legal_actions if 'CHECK' in x]
                        if checking_action:
                            return 'CHECK'
                        return 'FOLD'
                    r, lo, hi = raising_action[0].split(':')
                    lo = int(lo)
                    hi = int(hi)
                    bet_amt = max(min(int(random() * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt
                else:
                    checking_action = [x for x in legal_actions if 'CHECK' in x]
                    if checking_action:
                        return 'CHECK'
                    return 'FOLD'



        ############################## Case 4 ##################################
        ########################################################################
        # Not big blind two players

        if numActivePlayers == 2 and firstRound and ((seat == 1 and State.num_active == 2) or \
                (seat == 2 and State.num_active == 3)):
            if hand_score > (PLAY_PREFLOP + .4) * State.looseness:
                # Then we are going to CALL / RAISE

                # This is the case where we must call and cannot raise
                raising_action = [x for x in legal_actions if 'RAISE' in x]
                if len(raising_action) == 0:
                    call_action = [x for x in legal_actions if 'CALL' in x]
                    if not call_action:
                        return 'CHECK'
                    return call_action[0]

                # Deciding to raise
                if hand_score > .7:
                    # We are raising if we are good enough
                    raising_action = [x for x in legal_actions if 'RAISE' in x][0]
                    r, lo, hi = raising_action.split(':')
                    lo = int(lo)
                    hi = int(hi)

                    if hand_score < .75:
                        return 'RAISE:%d' % lo

                    bet_amt = max(min(int(hand_score * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt


                else:
                    call_action = [x for x in legal_actions if 'CALL' in x]
                    # Should not happen
                    if not call_action:
                        return 'CHECK'
                    return call_action[0]

                call_action = [x for x in legal_actions if 'CALL' in x]
                # Should not happen
                if not call_action:
                    return 'CHECK'
                return call_action[0]

            else:
                # Normally fold, but randomly raise
                if random() < .1:
                    # Randomly raise here
                    raising_action = [x for x in legal_actions if 'RAISE' in x]
                    if not raising_action:
                        return 'FOLD'
                    r, lo, hi = raising_action[0].split(':')
                    lo = int(lo)
                    hi = int(hi)
                    bet_amt = max(min(int(random() * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt
                else:
                    return 'FOLD'





        ############################## Case 5 ##################################
        ########################################################################
        # Big Blind two handed
        # TODO: fill in the logic here
        if numActivePlayers == 2 and firstRound and ((seat == 3 and State.num_active == 2) or \
                (seat == 3 and State.num_active == 3)):
            # TODO: Consider if we are facing a raise already
            if hand_score > PLAY_PREFLOP * State.looseness:
                # Then we are going to CALL / RAISE

                # This is the case where we must call and cannot raise
                raising_action = [x for x in legal_actions if 'RAISE' in x]
                if len(raising_action) == 0:
                    call_action = [x for x in legal_actions if 'CALL' in x]
                    if not call_action:
                        return 'CHECK'
                    return call_action[0]

                # Deciding to raise
                if hand_score > .7:
                    # We are raising if we are good enough
                    raising_action = [x for x in legal_actions if 'RAISE' in x][0]
                    r, lo, hi = raising_action.split(':')
                    lo = int(lo)
                    hi = int(hi)

                    if hand_score < .75:
                        return 'RAISE:%d' % lo

                    bet_amt = max(min(int(hand_score * hi * State.aggressiveness), hi), lo)
                    return 'RAISE:%d' % bet_amt


                else:
                    call_action = [x for x in legal_actions if 'CALL' in x]
                    if not call_action:
                        return 'CHECK'
                    return call_action[0]

                call_action = [x for x in legal_actions if 'CALL' in x]
                if not call_action:
                    return 'CHECK'
                return call_action[0]

            else:
                # Normally check/fold, but randomly raise
                if random() < .1:
                    # Randomly raise here
                    raising_action = [x for x in legal_actions if 'RAISE' in x]
                    if not raising_action:
                        checking_action = [x for x in legal_actions if 'CHECK' in x]
                        if checking_action:
                            return 'CHECK'
                        return 'FOLD'
                    r, lo, hi = raising_action[0].split(':')
                    lo = int(lo)
                    hi = int(hi)
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
        if not firstRound and 'CALL' in prev_actions[0]:
            # Play the pot odds
            call_action = [x for x in legal_actions if 'CALL' in x][0]
            call_amt = int(call_action.split(':')[-1])
            pot_size = potSize

            pot_odds = float(call_amt) / (2 * call_amt + potSize)

            if pot_odds < hand_score * .25:
                call_action = [x for x in legal_actions if 'CALL' in x]
                if not call_action:
                    return 'CHECK'
                return call_action[0]
            else:
                return 'FOLD'


        ############################## Case 7 ##################################
        ########################################################################
        # Second round and we raised last time
        # TODO: Logic
        if not firstRound and 'CALL' not in prev_actions[0]:
            # Play the pot odds
            call_action = [x for x in legal_actions if 'CALL' in x][0]
            call_amt = int(call_action.split(':')[-1])
            pot_size = potSize

            pot_odds = float(call_amt) / (2 * call_amt + potSize)

            if pot_odds < hand_score:
                call_action = [x for x in legal_actions if 'CALL' in x]
                if not call_action:
                    return 'CHECK'
                return call_action[0]
            else:
                return 'FOLD'



        return 'CHECK'
