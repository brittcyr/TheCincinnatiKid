from lib.hand_eval import convert_string_to_int, score_best_five, eval_hand
from lib.board_correlation import straight_correlation, flush_correlation
from Global import State
from random import random


def quick_check_if_hole_helps(score, board):
    if len(board) == 3:
        board = board + [-1, -6]
    elif len(board) == 4:
        board = board + [-1]
    that_score = eval_hand(board)
    if that_score[0] == score[0]:
        return False
    return True

def split_raise(legal_actions):
    raising_action = [x for x in legal_actions if 'RAISE' in x or 'BET' in x]
    if not raising_action:
        return False, False
    r, lo, hi = raising_action[0].split(':')
    lo = int(lo)
    hi = int(hi)
    return lo, hi

def classify_pair_flop(board, score):
    board = sorted([x / 4 for x in board])
    if score[1] < board[0]: return 0
    if score[1] == board[0]: return 1
    if score[1] > board[0] and score[1] < board[1]: return 2
    if score[1] == board[1]: return 3
    if score[1] > board[1] and score[1] < board[2]: return 4
    if score[1] == board[2]: return 5
    if score[1] > board[1] and score[1] < board[2]: return 6
    return -1

DECK = 52
def count_drawing_outs(hole, board):
    outs = 0
    for card in range(DECK):
        if card in hole or card in board: continue
        if score_best_five(hole + board + [card]) >= THREE_OF_A_KIND:
            outs += 1
    return outs


VAL_OF_OUT = .02127 # 1 / 47
PAIR_ODDS = {0: .1, 1: .2, 2: .4, 3: .6, 4: .7, 5: .9, 6: 1.0}
HIGH_CARD = 0
PAIR = 1
TWO_PAIR = 2
THREE_OF_A_KIND = 3
STRAIGHT = 4
FLUSH = 5
FULL_HOUSE = 6


class Flop(object):

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

        # These are the variables based on position
        score = score_best_five(board_cards + State.hole_cards)


        # CHECK / BET           1
        # CALL / FOLD / RAISE   2


        #######################################################################
        # Case 1
        #######################################################################
        # Nobody else has acted
        if any([x for x in legal_actions if 'CHECK' in x]):
            bet_prob = 0

            # We bet if we have more than a pair
            if score[0] > PAIR and quick_check_if_hole_helps(score, board_cards):
                bet_prob = 1
            elif score[0] == PAIR and quick_check_if_hole_helps(score, board_cards):
                val = classify_pair_flop(board_cards, score)
                bet_prob = PAIR_ODDS[val]
            elif score[0] == HIGH_CARD:
                bet_prob += max(State.hole_cards) / 4 * .02
            else:
                # This is our kicker to a pair on the board
                bet_prob = max(State.hole_cards) / 4 * .01

            if random() < bet_prob:
                lo, hi = split_raise(legal_actions)
                if score[0] >= STRAIGHT:
                    return 'BET:%d' % hi

                if score[0] >= TWO_PAIR:
                    bet_amt = max(min(int((.25 + random()) * hi * State.aggressiveness), hi), lo)
                    return 'BET:%d' % bet_amt

                if score[0] >= PAIR:
                    bet_amt = max(min(int(bet_prob * hi * State.aggressiveness), hi), lo)
                    return 'BET:%d' % bet_amt

                return 'BET:%d' % lo
            else:
                # Bluff at scary board
                if max(flush_correlation(board_cards), straight_correlation(board_cards)) >= 3:
                    if random() > BLUFF_AT_SCARY_BOARD:
                        lo, hi = split_raise(legal_actions)
                        if not lo: return 'CHECK'
                        return 'BET:%d' % lo

                return 'CHECK'


        # Case 2
        #######################################################################
        # Need to decide if we should FOLD / CALL / RAISE
        if any([x for x in legal_actions if 'CALL' in x]):
            # Compute pot odds
            call_action = [x for x in legal_actions if 'CALL' in x][0]
            call_amt = int(call_action.split(':')[-1])
            pot_size = potSize

            pot_odds = float(call_amt) / (2 * call_amt + potSize)

            # Determine what the odds of winning are by guessing
            guessed_win_prob = 0
            if score[0] == HIGH_CARD:
                guessed_win_prob = float(score[1][0] / 13) / 40

            if score[0] <= TWO_PAIR:
                # PAIR
                if score[0] == PAIR:
                    val = classify_pair_flop(board_cards, score)
                    guessed_win_prob += PAIR_ODDS[val]

                # TWO PAIR
                elif score[0] == TWO_PAIR:
                    guessed_win_prob += .7
                    guessed_win_prob += .05 * score[1]

                # Drop our odds if there is a scary board
                if max(flush_correlation(board_cards), straight_correlation(board_cards)) >= 3:
                    guessed_win_prob *= .5

                # Consider draws as good
                guessed_win_prob = max(guessed_win_prob, \
                        VAL_OF_OUT * count_drawing_outs(State.hole_cards, board_cards))

                if pot_odds < guessed_win_prob:
                    prev_bets = [x for x in prev_actions if 'RAISE' in x or 'BET' in x]
                    multibet = len(prev_bets) >= 2
                    if pot_odds < 2 * guessed_win_prob and not multibet:
                        lo, hi = split_raise(legal_actions)
                        if not lo: return call_action

                        if pot_odds > 4 * guessed_win_prob:
                            bet_amt = max(min(int(random() * 2 * lo * State.aggressiveness), hi), lo)
                        else:
                            bet_amt = max(min(int(random() * hi * State.aggressiveness), hi), lo)
                        return 'RAISE:%d' % bet_amt
                    return call_action
                return 'FOLD'

            lo, hi = split_raise(legal_actions)
            if not lo: return call_action

            if score[0] >= FULL_HOUSE or score[0] == STRAIGHT:
                return 'RAISE:%d' % hi

            if score[0] == FLUSH:
                bet_amt = max(min(int(score[1] * .9 * hi * State.aggressiveness), hi), lo)
                return 'RAISE:%d' % bet_amt

            if score[0] == THREE_OF_A_KIND and quick_check_if_hole_helps(score, board_cards):
                bet_amt = max(min(int(random() * hi * State.aggressiveness), hi), lo)
                return 'RAISE:%d' % bet_amt

            return call_action

        return 'CHECK'
