"""
This is a library of hand heuristic evaluator helpers. These functions
are used in the intermediate evaluation of hand quality to decide
whether or not to play a hand and how to play it.
"""

def is_three_of_a_kind(hole_cards, board):
    """check if there is a three of a kind

    Determine whether there is a three of a kind using at least one
    hole card

    Args:
        hole_cards: sorted list of cards in integer form
        board: sorted list of cards in integer form

    Returns:
        boolean whether or not there is a three of a kind
    """
    # This checks if there are three of a kind using a board card
    hole_cards = [card / 4 for card in hole_cards]
    board = [card / 4 for card in board]

    for card in board:
        # We dont want to use more than two cards from the board
        if min(2, board.count(card)) + min(2, hole_cards.count(card)) >= 3:
            return True
    return False

def is_two_pair(hole_cards, board):
    """check if there is a two pair

    Determine whether there is two pair using two hole cards

    Args:
        hole_cards: sorted list of cards in integer form
        board: sorted list of cards in integer form

    Returns:
        boolean whether or not there is a three of a kind
    """
    hole_cards = [card / 4 for card in hole_cards]
    board = [card / 4 for card in board]

    pairs = 0
    for card in hole_cards:
        occurrences = board.count(card)
        if occurrences >= 1:
            # We have a pair
            pairs += 1

    return pairs >= 2

def is_pair(hole_cards, board):
    """check if there is a pair

    Determine whether there is pair using at least one hole card

    Args:
        hole_cards: sorted list of cards in integer form
        board: sorted list of cards in integer form

    Returns:
        boolean whether or not there is a three of a kind
    """
    hole_cards = [card / 4 for card in hole_cards]
    board = [card / 4 for card in board]

    for card in hole_cards:
        occurrences = board.count(card) + hole_cards.count(card) - 1
        if occurrences >= 1:
            # We have a pair
            return True

    return False

def is_full_house(hole_cards, board):
    """check if there is a full house

    Determine whether there is a full house, does not work
    on the flop, but not necessary since then is three of a kind

    Args:
        hole_cards: sorted list of cards in integer form
        board: sorted list of cards in integer form

    Returns:
        boolean whether or not there is a three of a kind
    """
    hole_cards = [card / 4 for card in hole_cards]
    board = [card / 4 for card in board]

    if len(hole_cards) == 3:
        return False

    cards = hole_cards + board
    counts = [cards.count(card) for card in cards]

    # Regular Full house
    if 2 in counts and 3 in counts:
        return True

    # Actually a four of a kind
    if 2 in counts and 4 in counts:
        return True

    # Actually a four of a kind with full house on board
    if 3 in counts and 4 in counts:
        return True

    if counts.count(3) > 3:
        return True

    return False

def cards_to_straight(hole_cards, board):
    """check how far we are from a straight

    Consider all possible straights and see how many cards we would need to
    get a straight for each

    Args:
        hole_cards: sorted list of cards in integer form
        board: sorted list of cards in integer form

    Returns:
        3-tuple, the first index is the number of straights, the second is the
        number of straights we need one card to get, and the final index is the
        number of straights we need two cards to get.
    """
    hole_cards = [card / 4 for card in hole_cards]
    board = [card / 4 for card in board]

    vals = [5] * 10
    for start in range(9):
        hand_cards = 0
        missing = 0
        for ind in range(start, start + 5):
            if not ind in board:
                # This makes sure that we don't use three hole cards in straight
                if (not (ind in hole_cards)) or hand_cards == 2:
                    missing += 1
                else:
                    hand_cards += 1
        vals[start] = missing

    # separately consider wheel
    vals[9] = 0 if 12 in hole_cards + board else 1
    hand_cards = 0
    for ind in range(4):
        if not ind in board:
            if (not (ind in hole_cards)) or hand_cards == 2:
                vals[9] += 1
            else:
                hand_cards += 1

    return (vals.count(0), vals.count(1), vals.count(2))

def cards_to_flush(hole_cards, board):
    """check how far we are from a flush

    Consider all possible flushes and see how many cards we would need for one

    Args:
        hole_cards: sorted list of cards in integer form
        board: sorted list of cards in integer form

    Returns:
        integer, the minimum number of cards to get a flush
    """
    hole_cards = [card % 4 for card in hole_cards]
    board = [card % 4 for card in board]

    cards_needed = [5, 5, 5, 5]

    for suit in xrange(4):
        number = min(hole_cards.count(suit), 2) + board.count(suit)
        cards_needed[suit] = max(5 - number, 0)

    # We only care about our best suit because there will never be more than
    # one flush opportunity after the discard since that requires too many cards
    return min(cards_needed)

def has_top_pair(hole_cards, board):
    """check if there is a top pair

    Determine whether there is top pair using at least one hole card

    Args:
        hole_cards: sorted list of cards in integer form
        board: sorted list of cards in integer form

    Returns:
        boolean whether or not there is a top pair
    """
    hole_cards = [card / 4 for card in hole_cards]
    board = [card / 4 for card in board]

    if hole_cards.count(board[-1]) >= 1:
        return True
    return False

def has_over_pair(hole_cards, board):
    """check if there is an over pair

    Determine whether there is an over pair using hole cards

    Args:
        hole_cards: sorted list of cards in integer form
        board: sorted list of cards in integer form

    Returns:
        boolean whether or not there is an over pair
    """
    hole_cards = [card / 4 for card in hole_cards]
    board = [card / 4 for card in board]

    for ind in xrange(len(hole_cards) - 1):
        if hole_cards[ind] == hole_cards[ind + 1]:
            if hole_cards[1] > board[-1]:
                return True
    return False

def has_under_pair(hole_cards, board):
    """check if there is an under pair

    Determine whether there is an under pair using hole cards

    Args:
        hole_cards: sorted list of cards in integer form
        board: sorted list of cards in integer form

    Returns:
        boolean whether or not there is an under pair
    """
    hole_cards = [card / 4 for card in hole_cards]
    board = [card / 4 for card in board]
    for ind in xrange(len(hole_cards) - 1):
        if hole_cards[ind] == hole_cards[ind + 1]:
            if hole_cards[1] < board[0]:
                return True
    return False

def high(hole_cards, _board):
    """get the high card

    Find the highest valued card in the hole cards

    Args:
        hole_cards: sorted list of cards in integer form
        board: sorted list of cards in integer form

    Returns:
        integer for highest value in the hole_cards
    """
    hand = [card / 4 for card in hole_cards]
    return max(hand)

def is_pair_high(cards, threshold):
    """check if there is a sufficiently high pair

    Determine whether there is a pair of at least high

    Args:
        cards: sorted list of cards in integer form
        threshold: integer for minimum value of pair

    Returns:
        boolean whether or not there is a high enough pair
    """
    cards = [card / 4 for card in cards]
    cards.sort()
    if cards[0] == cards[1] or cards[1] == cards[2]:
        if cards[1] >= threshold:
            return True
    return False

def suited_high_card(cards, threshold):
    """check if there is a sufficiently high suited card

    Determine whether there is a suited card of at least high, with the
    exception if we are triple suited and then the other cards are low

    Args:
        cards: sorted list of cards in integer form
        threshold: integer for minimum value of pair

    Returns:
        boolean whether or not there is a high enough suited card
    """
    cards.sort()
    if cards[2] / 4 >= threshold:
        if cards[2] % 4 == cards[1] % 4:
            if cards[2] % 4 == cards[0] % 4:
                if cards[1] >= threshold - 3:
                    return True
            else:
                return True
        elif cards[2] % 4 == cards[0] % 4:
            if cards[2] % 4 == cards[1] % 4:
                if cards[1] >= threshold - 3:
                    return True
            else:
                return True
    if cards[1] / 4 >= threshold:
        if cards[1] % 4 == cards[0] % 4:
            return True
    return False

def three_to_straight(cards):
    """check if there is three to a straight

    Determine whether there is a set of hole cards that requires only two
    more cards to make a straight, but does not contain a connector

    Args:
        cards: list of cards in integer form

    Returns:
        boolean whether or not there is three to a straight
    """
    cards.sort()
    cards = [card / 4 for card in cards]
    if cards[0] + 4 >= cards[2]:
        return True

    if cards[2] == 12 and cards[1] == 3:
        return True

    return False

def high_cards(cards, threshold):
    """check if there are high enough card

    Determine whether there is a card greater than or equal to high

    Args:
        cards: list of cards in integer form
        threshold: integer threshold for the highest card

    Returns:
        boolean whether or not there is a high enough card
    """
    cards.sort()
    cards = [card / 4 for card in cards]
    if cards[2] >= threshold:
        return True
    return False

def connector(cards):
    """check if there is connectors

    Determine whether there is a set of hole cards that are adjacent

    Args:
        cards: list of cards in integer form

    Returns:
        boolean whether or not there is connectors
    """
    cards.sort()
    cards = [card / 4 for card in cards]
    if cards[1] == cards[2] - 1 or cards[1] == cards[0] + 1:
        return True
    if cards[-1] == 12 and cards[0] == 0:
        return True
    return False
