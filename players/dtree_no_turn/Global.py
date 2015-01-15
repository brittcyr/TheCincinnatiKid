from lib.hand_eval import convert_string_to_int

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
    check_fold_to_win = False


    @classmethod
    def consider_time_of_game(cls):
        # My stack is stackSize
        stacks = [cls.stack1, cls.stack2, cls.stack3]
        stacks.pop(stacks.index(cls.stackSize))
        rest = sum(stacks)

        # If we should CHECK/FOLD, then just adjust the looseness
        check_to_lost_amt = (cls.num_hands - cls.handId) * ((int(cls.bb) * 3 / 2) + 1)
        if check_to_lost_amt < cls.stackSize - rest:
            cls.check_fold_to_win = True
            cls.aggressiveness = 0.0
            cls.looseness = 0.0
            return

        # If we need to late game gamble, then increase aggressiveness
        THRESHOLD = 5
        # If we are late and need more than threshold bb's per hand
        # to win all the chips, then increase aggressiveness
        if (rest - cls.stackSize) / (cls.num_hands - cls.handId) > THRESHOLD * cls.bb:
            cls.aggressiveness += .1
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

        numLastActions = int(data.pop(0))
        for _ in range(numLastActions):
            data.pop(0)

        cls.timeBank = float(data.pop(0))

        # TODO: Decide how to adjust aggressiveness and looseness
        # If we win by being aggressive preflop, increase aggressiveness and looseness
        # If we lose by being aggressive preflop, increase aggressiveness and looseness
