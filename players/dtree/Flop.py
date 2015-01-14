from lib.hand_eval import convert_string_to_int, score_best_five
from Global import State
from random import random


class Flop(object):

    @classmethod
    def get_action(cls, data):
        # GETACTION potSize numBoardCards [boardCards] [stackSizes] numActivePlayers [activePlayers] numLastActions [lastActions] numLegalActions [legalActions] timebank
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


        # These are the variables based on position
        seat = State.seat
        numActivePlayers = numActivePlayers
        score = score_best_five(board_cards + State.hole_cards)


        # The logic will be to consider the probability that we win and compute
        # First the pot odd, then the implied odds, then the fold equity

        # CHECK / BET
        # CALL / FOLD / RAISE



        # Case 1
        #######################################################################
        # Nobody else has acted

        # TODO: consider fold equity for betting and reverse pot odds
        if any([x for x in legal_actions if 'CHECK' in x]):
            # Determine if we should show strength and how much

            # If we have a hand, then bet, if we don't then do not
            bet_prob = 0

            # We bet if we have more than a pair
            if score[0] > 1:
                bet_prob = 1
            elif score[0] == 1:
                val_of_pair = score[1]
                # val_of_pair goes from 0 - 12
                bet_prob += .28
                bet_prob += val_of_pair * .03
            elif score[0] == 0:
                bet_prob += score[1][0] * .01

            if random() < bet_prob:
                betting_action = [x for x in legal_actions if 'BET' in x]
                if not betting_action:
                    return 'CHECK'
                b, lo, hi = betting_action[0].split(':')
                lo = int(lo)
                hi = int(hi)

                # BET
                if score[0] >= 4:
                    # Max bet with a straight or better
                    bet_amt = hi
                    return 'BET:%d' % bet_amt

                if score[0] >= 2:
                    bet_amt = max(min(int((.25 + random()) * hi * State.aggressiveness), hi), lo)
                    return 'BET:%d' % bet_amt

                if score[0] >= 1:
                    bet_amt = max(min(int((.05 * score[1]) * hi * State.aggressiveness), hi), lo)
                    return 'BET:%d' % bet_amt

                bet_amt = lo
                return 'BET:%d' % bet_amt
            else:
                return 'CHECK'


        # Case 2
        #######################################################################
        # Need to decide if we should FOLD / CALL / RAISE
        # TODO: Consider if we are facing multiple bets. Tune this

        if any([x for x in legal_actions if 'CALL' in x]):
            # Compute pot odds
            call_action = [x for x in legal_actions if 'CALL' in x][0]
            call_amt = int(call_action.split(':')[-1])
            pot_size = potSize

            pot_odds = float(call_amt) / (2 * call_amt + potSize)

            # Determine what the odds of winning are by guessing
            guessed_win_prob = 0
            if score[0] == 0:
                guessed_win_prob = float(score[1][0] / 13) / 40

            if score[0] <= 2:
                # PAIR
                if score[0] == 1:
                    guessed_win_prob += .05 * score[1]

                # TWO PAIR
                if score[0] == 2:
                    guessed_win_prob += .7
                    guessed_win_prob += .05 * score[1]

                if pot_odds < guessed_win_prob:
                    prev_bets = [x for x in prev_actions if 'RAISE' in x or 'BET' in x]

                    # TODO: Reconsider this. Do not increase pot if there are two bets
                    # until we are sure we have a better hand evaluator
                    multibet = len(prev_bets) >= 2
                    if pot_odds < 2 * guessed_win_prob and not multibet:
                        # Raise if we have double the odds to call
                        betting_action = [x for x in legal_actions if 'RAISE' in x]
                        if not betting_action:
                            return call_action
                        b, lo, hi = betting_action[0].split(':')
                        lo = int(lo)
                        hi = int(hi)
                        if pot_odds > 4 * guessed_win_prob:
                            bet_amt = max(min(int(random() * 2 * lo * State.aggressiveness), hi), lo)
                        else:
                            bet_amt = max(min(int(random() * hi * State.aggressiveness), hi), lo)
                        return 'RAISE:%d' % bet_amt
                    else:
                        # Just enough to call but not raise
                        return call_action

                return 'FOLD'


            betting_action = [x for x in legal_actions if 'RAISE' in x]
            if not betting_action:
                return call_action
            b, lo, hi = betting_action[0].split(':')
            lo = int(lo)
            hi = int(hi)

            # FULL HOUSE or better is always max raise
            if score[0] >= 6:
                return 'RAISE:%d' % hi

            # FLUSH
            if score[0] == 5:
                # If the kicker is high enough
                if score[1] >= 10:
                    return 'RAISE:%d' % hi
                else:
                    if random() < score[1] * .1:
                        bet_amt = max(min(int(random() * hi * State.aggressiveness), hi), lo)
                        return 'RAISE:%d' % bet_amt
                    else:
                        return call_action

            # STRAIGHT
            if score[0] == 4:
                # If the kicker is high enough
                if score[1] >= 10:
                    return 'RAISE:%d' % hi
                return call_action


            # Otherwise we want to get the pot bigger
            if pot_odds < 2 * guessed_win_prob:
                bet_amt = max(min(int(random() * hi * State.aggressiveness), hi), lo)
                return 'RAISE:%d' % bet_amt

            return call_action


        return 'CHECK'
