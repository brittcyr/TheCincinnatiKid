from lib.hand_eval import convert_string_to_int, score_best_five
import subprocess
import os
import os.path


class State(object):
    # Aggressiveness is a multiplier for the bet
    aggressiveness = 1.0

    # Looseness is a parameter that tunes how many hands we play
    # it is a multiplier of the cutoff threshold
    looseness = 1.0

    hole_cards = [-1, -1]
    board = []
    num_hands = 0
    bb = 0
    opp1Name = ''
    opp2Name = ''
    stackSize = 0
    timeBank = 0
    handId = 0
    seat = 0
    stack1 = 0
    stack2 = 0
    stack3 = 0
    num_active = 0
    total_hands_played = 0
    check_fold_to_win = False
    hand_actions = []
    deck = []
    names = []
    current_result = None


    @classmethod
    def consider_time_of_game(cls):
        # My stack is stackSize
        stacks = [cls.stack1, cls.stack2, cls.stack3]
        stacks.pop(stacks.index(cls.stackSize))
        rest = sum(stacks)

        # If we are losing and we are close to second to last
        if cls.stackSize == min(stacks) and \
                cls.stackSize < 30 * int(cls.bb) and \
                sorted(stacks)[1] < cls.stackSize + 10 * int(cls.bb):
            cls.looseness -= .005

        # If we should CHECK/FOLD, then just adjust the looseness
        check_to_lost_amt = (cls.num_hands - cls.handId) * ((int(cls.bb) * 3 / 2) + 1)
        if 2 * check_to_lost_amt < cls.stackSize - rest:
            cls.check_fold_to_win = True
            cls.aggressiveness = 0.0
            cls.looseness = 0.0
            return

        # Final Hand, go for broke
        if cls.num_hands == cls.handId:
            cls.aggressiveness = 10
            cls.looseness = 10
            return

        # If we need to late game gamble, then increase aggressiveness
        THRESHOLD = 5
        # If we are late and need more than threshold bb's per hand
        # to win all the chips, then increase aggressiveness
        if (rest - cls.stackSize) / (cls.num_hands - cls.handId) > THRESHOLD * cls.bb:
            cls.aggressiveness += .1
            return

        # If we are down to less than 8 big blinds, go for broke. This should
        # probably be turned off later, but if it worked, then stick with it.
        if cls.bb * 8 > cls.stackSize:
            cls.aggressiveness *= 2
            cls.looseness *= 2
            return

        # If I have lots more than the rest of the table
        if 2 * rest < cls.stackSize:
            cls.looseness = .7
            return

    @classmethod
    def new_game(cls, data):
        new_game, yourName, opp1Name, opp2Name, stackSize, bb, \
                numHands, timeBank = data.split()
        # NEWGAME yourName opp1Name opp2Name stackSize bb numHands timeBank
        cls.opp1Name = opp1Name
        cls.opp2Name = opp2Name
        cls.stackSize = int(stackSize)
        cls.bb = int(bb)
        cls.num_hands = int(numHands)
        cls.timeBank = float(timeBank)
        cls.check_fold_to_win = False

        cls.looseness = 1.0
        cls.aggressiveness = 1.0



        # Only do this on the first time around
        if not cls.deck:
            round_num = 0

            try:
                path = os.getcwd()
                os.chdir(os.path.dirname(os.path.realpath(__file__)))
                print 'NAMES', [opp1Name, yourName, opp2Name]
                names, round_num = decode_names([opp1Name, yourName, opp2Name])
                print 'NAMES', names
                print 'ROUND', round_num
                if round_num == None:
                    round_num = -1

                sp = subprocess.Popen(['java', 'DeckDecoder', names[0], \
                        names[1], names[2], str(round_num), \
                        str(cls.num_hands + 1000)], stdout=subprocess.PIPE, \
                        stderr=subprocess.PIPE)
                out, err = sp.communicate()

                hands = out.replace('[', '').replace(']', '').split('\n')
                cls.deck = [x.replace(' ', '').split(',') for x in hands]
                cls.names = names
                cls.round_num = round_num

            except Exception as e:
                print e

            os.chdir(path)



    @classmethod
    def new_hand(cls, data):
        # NEWHAND handId seat holeCard1 holeCard2 [stackSizes] [playerNames] numActivePlayers [activePlayer    s] timeBank
        new_hand, handId, seat, holeCard1, holeCard2, stackSize1, stackSize2, stackSize3, \
                playerName1, playerName2, playerName3, numActivePlayers, \
                activePlayer1, activePlayer2, activePlayer3, timeBank = data.split()

        cls.handId = int(handId)
        cls.seat = int(seat)
        cls.stack1 = int(stackSize1)
        cls.stack2 = int(stackSize2)
        cls.stack3 = int(stackSize3)

        # Update my stack size
        if cls.seat == 1:
            cls.stackSize = cls.stack1
        elif cls.seat == 2:
            cls.stackSize = cls.stack2
        elif cls.seat == 3:
            cls.stackSize = cls.stack3

        cls.num_active = int(numActivePlayers)
        cls.timeBank = float(timeBank)
        hole_card1 = convert_string_to_int(holeCard1)
        hole_card2 = convert_string_to_int(holeCard2)
        cls.hole_cards = sorted([hole_card1, hole_card2])

        State.consider_time_of_game()
        cls.hand_actions = []
        cls.current_result = None
        hand = cls.deck[cls.total_hands_played]
        cls.total_hands_played += 1

        print hand
        hand = [convert_string_to_int(x) for x in hand]
        print hand
        print 'HOLE CARDS', cls.hole_cards

        if cls.hole_cards[0] not in hand[0:6] or cls.hole_cards[1] not in hand[0:6]:
            print 'Round num and num hands', cls.round_num, cls.num_hands
            if (cls.num_hands - cls.handId) * .05 <= cls.timeBank:
                try:
                    path = os.getcwd()
                    os.chdir(os.path.dirname(os.path.realpath(__file__)))
                    cls.round_num += 1
                    sp = subprocess.Popen(['java', 'DeckDecoder', cls.names[0], \
                            cls.names[1], cls.names[2], str(cls.round_num), \
                            str(cls.num_hands + 1000)], stdout=subprocess.PIPE, \
                            stderr=subprocess.PIPE)

                    out, err = sp.communicate()
                    os.chdir(path)

                    hands = out.replace('[', '').replace(']', '').split('\n')
                    cls.deck = [x.replace(' ', '').split(',') for x in hands]
                    print 'Trying new deck', cls.deck[cls.total_hands_played - 1], cls.round_num
                except Exception as e:
                    print e
        else:
            print 'I think I got it', hand, cls.hole_cards
            hole1 = [hand[0], hand[3]]
            hole2 = [hand[1], hand[4]]
            hole3 = [hand[2], hand[5]]
            score1 = score_best_five(hand[6:] + hole1)
            score2 = score_best_five(hand[6:] + hole2)
            score3 = score_best_five(hand[6:] + hole3)
            # TODO: Check it against the list of who is playing in the hand
            if set(cls.hole_cards) == set(hole1):
                if score1 >= score2 and score1 >= score3:
                    # I win
                    print 'I win', hole1, score1
                    cls.current_result = True
                else:
                    # I lose
                    print 'I lose', hole1, score1
                    cls.current_result = False

            elif set(cls.hole_cards) == set(hole2):
                if score2 >= score1 and score2 >= score3:
                    # I win
                    print 'I win', hole2, score2
                    cls.current_result = True
                else:
                    # I lose
                    print 'I lose', hole2, score2
                    cls.current_result = False

            elif set(cls.hole_cards) == set(hole3):
                if score3 >= score1 and score3 >= score2:
                    # I win
                    print 'I win', hole3, score3
                    cls.current_result = True
                else:
                    # I lose
                    print 'I lose', hole3, score3
                    cls.current_result = False
            else:
                print 'I couldnt guess hand', cls.hole_cards, hand


    @classmethod
    def handover(cls, data):
        # HANDOVER [stackSizes] numBoardCards [boardCards] numLastActions [lastActions] timeBank
        data = data.split()
        handover = data.pop(0)
        cls.stack1 = int(data.pop(0))
        cls.stack2 = int(data.pop(0))
        cls.stack3 = int(data.pop(0))
        numBoardCards = int(data.pop(0))
        for _ in range(numBoardCards):
            data.pop(0)

        last_actions = []
        numLastActions = int(data.pop(0))
        for _ in range(numLastActions):
            last_actions.append(data.pop(0))
        cls.hand_actions += last_actions

        cls.timeBank = float(data.pop(0))

        print cls.hand_actions


def java_string_hashcode(s):
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF
    return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000


def decode_names(names):
    names = [int(x[:-1]) for x in names]
    results = []

    teams = []
    f = open('./teams', 'r')
    for line in f:
        teams.append(line.strip())
    f.close()

    for team in teams:
        salt = "randomstring"
        prehash = team + salt
        seed = abs(java_string_hashcode(prehash))
        if seed in names:
            results.append(team)
        if len(results) == 3:
            return results, None

    for rnd in xrange(100):
        for team in teams:
            salt = "randomstring"
            prehash = team + str(rnd) + salt
            seed = abs(java_string_hashcode(prehash))
            if seed in names:
                results.append(team)

            if len(results) == 3:
                return results, rnd

    return ['TheCincinnatiKid', 'TheHouse', 'CJK'], 0
