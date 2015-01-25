from lib.hand_eval import convert_string_to_int, score_best_five, eval_hand, \
        count_drawing_outs
from lib.board_correlation import straight_correlation, flush_correlation
from Global import State
from random import random


def try_to_check(legal_actions):
    check_action = [x for x in legal_actions if 'CHECK' in x]
    if not check_action:
        return 'FOLD'
    return check_action[0]

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

def classify_pair_turn(board, score):
    board = sorted([x / 4 for x in board])
    if score[1] > board[3]: return 8
    if score[1] == board[3]: return 7
    if score[1] > board[2] and score[1] < board[3]: return 6
    if score[1] == board[2]: return 5
    if score[1] > board[1] and score[1] < board[2]: return 4
    if score[1] == board[1]: return 3
    if score[1] > board[0] and score[1] < board[1]: return 2
    if score[1] == board[0]: return 1
    if score[1] < board[0]: return 0
    return 0

def board_correlation(board_cards):
    return max(flush_correlation(board_cards), \
            straight_correlation(board_cards))

NOT_PAIRED_BOARD = -1
def paired_board(board):
    board = sorted([x / 4 for x in board])
    if board[1] == board[0] or board[1] == board[2]:
        return board[1]
    if board[2] == board[3]:
        return board[2]
    return NOT_PAIRED_BOARD


VAL_OF_OUT = .02174 # 1 / 46
PAIR_ODDS = {0: .1, 1: .15, 2: .2, 3: .25, 4: .3, 5: .3, 6: .55, 7: .7, 8: .9}
HIGH_CARD = 0
PAIR = 1
TWO_PAIR = 2
THREE_OF_A_KIND = 3
STRAIGHT = 4
FLUSH = 5
FULL_HOUSE = 6

BLUFF_AT_SCARY_BOARD = .05
BLUFF_AT_REALLY_SCARY_BOARD = .15


class Turn(object):

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

        if numLegalActions == 1:
            return legal_actions[0]

        State.timebank = float(data.pop(0))

        # These are the variables based on position
        score = score_best_five(board_cards + State.hole_cards)
        i_called = 'CALL' in prev_actions[0]

        print 'Turn score', score

        # CHECK / BET           1
        # CALL / FOLD / RAISE   2


        ############################ Case 1 ###################################
        #######################################################################
        # Nobody else has bet
        if any([x for x in legal_actions if 'CHECK' in x]):
            lo, hi = split_raise(legal_actions)
            if not lo: return 'CHECK'

            # We bet if we have more than a pair
            if score[0] > PAIR and quick_check_if_hole_helps(score, board_cards):
                bet_prob = 1
            elif score[0] == PAIR and quick_check_if_hole_helps(score, board_cards):
                bet_prob = PAIR_ODDS[classify_pair_turn(board_cards, score)]
            else:
                # This is our kicker to a pair on the board or just high card
                bet_prob = max(State.hole_cards) / 4 * .01

            if random() < bet_prob:
                if score[0] >= STRAIGHT:
                    return 'BET:%d' % hi

                if score[0] >= TWO_PAIR:
                    if score[0] == TWO_PAIR and paired_board(board_cards) == score[1]:
                        return 'BET:%d' % lo
                    bet_amt = max(min(int(hi * State.aggressiveness), hi), lo)
                    return 'BET:%d' % bet_amt

                if board_correlation(board_cards) >= 3:
                    # Price out the flushes
                    nine_out_rev_pot_odds = .04 * 9
                    bet_amt = nine_out_rev_pot_odds * potSize / (1 - nine_out_rev_pot_odds)
                    bet_amt = max(min(int(bet_amt * State.aggressiveness), hi), lo)
                    return 'BET:%d' % bet_amt

                # If they raised into us and we called, then do not attack
                if i_called: return try_to_check(legal_actions)

                # Bet for at least middle pair
                if score[0] >= PAIR and quick_check_if_hole_helps(score, board_cards) and \
                        classify_pair_turn(board_cards, score) >= 5:
                    bet_amt = max(min(int(bet_prob * hi * State.aggressiveness), hi), lo)
                    return 'BET:%d' % bet_amt

                return 'BET:%d' % lo
            else:
                # Bluff at scary board
                if board_correlation(board_cards) >= 3:
                    if random() > BLUFF_AT_SCARY_BOARD:
                        bet_amt = max(min(int(2 * lo * State.aggressiveness), hi), lo)
                        print 'Turn bluff'
                        return 'BET:%d' % bet_amt

                if board_correlation(board_cards) >= 4 \
                        and not i_called:
                    if random() > BLUFF_AT_REALLY_SCARY_BOARD:
                        bet_amt = max(min(int(.25 * potSize * State.aggressiveness), hi), lo)
                        print 'Turn bluff'
                        return 'BET:%d' % bet_amt

                return 'CHECK'


        ############################ Case 2 ###################################
        #######################################################################
        # Need to decide if we should FOLD / CALL / RAISE
        if any([x for x in legal_actions if 'CALL' in x]):
            # Compute pot odds
            call_action = [x for x in legal_actions if 'CALL' in x][0]
            call_amt = int(call_action.split(':')[-1])

            pot_odds = float(call_amt) / (call_amt + potSize)
            # Determine what the odds of winning are by guessing
            if score[0] <= TWO_PAIR:
                guessed_win_prob = 0
                # HIGH CARD
                if score[0] == HIGH_CARD:
                    guessed_win_prob = float(score[1][0] / 4) / 60
                elif score[0] == PAIR:
                    val = classify_pair_turn(board_cards, score)
                    guessed_win_prob += PAIR_ODDS[val]
                    if not quick_check_if_hole_helps(score, board_cards):
                        guessed_win_prob *= .25
                elif score[0] == TWO_PAIR:
                    if paired_board(board_cards) != NOT_PAIRED_BOARD:
                        guessed_win_prob = .3
                        guessed_win_prob += .04 * (score[1] - paired_board(board_cards))
                    else:
                        guessed_win_prob += .6
                        guessed_win_prob += .04 * score[1]

                # Drop our odds if there is a scary board
                correlation = board_correlation(board_cards)
                if correlation >= 3:
                    guessed_win_prob *= .5
                if correlation >= 4:
                    guessed_win_prob *= .5

                # Consider draws as good
                guessed_win_prob = max(guessed_win_prob, \
                        VAL_OF_OUT * count_drawing_outs(State.hole_cards, board_cards))

                if pot_odds < guessed_win_prob:
                    prev_bets = [x for x in prev_actions if 'RAISE' in x or 'BET' in x]
                    multibet = len(prev_bets) >= 2
                    if 2 * pot_odds < guessed_win_prob and not multibet:
                        lo, hi = split_raise(legal_actions)
                        if not lo: return call_action

                        if 4 * pot_odds < guessed_win_prob:
                            bet_amt = max(min(int((1 + random()) / 2 * hi \
                                    * State.aggressiveness), hi), lo)
                        else:
                            bet_amt = max(min(int(lo * State.aggressiveness), hi), lo)

                        return 'RAISE:%d' % bet_amt
                    return call_action
                return 'FOLD'

            lo, hi = split_raise(legal_actions)
            if not lo: return call_action

            if score[0] >= STRAIGHT:
                prev_bets = [x for x in prev_actions if 'RAISE' in x or 'BET' in x]
                multibet = len(prev_bets) >= 2
                if quick_check_if_hole_helps(score, board_cards) and not multibet:
                    return 'RAISE:%d' % hi
                else:
                    return call_action

            if score[0] == THREE_OF_A_KIND and quick_check_if_hole_helps(score, board_cards):
                correlation = board_correlation(board_cards)
                if correlation >= 4:
                    bet_amt = lo
                else:
                    bet_amt = max(min(int((1 + random()) / 2 * hi * \
                            State.aggressiveness), hi), lo)
                return 'RAISE:%d' % bet_amt

            return call_action

        return 'CHECK'
