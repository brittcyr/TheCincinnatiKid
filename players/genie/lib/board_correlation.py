"""
This is a library of hand heuristic evaluator helpers. These functions
are used in the intermediate evaluation of hand quality to decide
whether or not to play a hand and how to play it.
"""

# This is to determine how many cards are needed for a straight
def straight_correlation(board):
    """figure out how close the board is to a straight

    Determine how many cards are needed for a straight

    Args:
        board: list of cards in integer form

    Returns:
        integer with the most cards in a possible straight
    """
    board = set([x / 4 for x in board])
    # Consider each of the 8 straights separately

    five_high = set([12, 0, 1, 2, 3])
    six_high = set([0, 1, 2, 3, 4])
    seven_high = set([1, 2, 3, 4, 5])
    eight_high = set([2, 3, 4, 5, 6])
    nine_high = set([3, 4, 5, 6, 7])
    ten_high = set([4, 5, 6, 7, 8])
    j_high = set([5, 6, 7, 8, 9])
    q_high = set([6, 7, 8, 9, 10])
    k_high = set([7, 8, 9, 10, 11])
    a_high = set([8, 9, 10, 11, 12])

    straights = [five_high, six_high, seven_high, eight_high, \
            nine_high, ten_high, j_high, q_high, k_high, a_high]

    return max([len(x.intersection(board)) for x in straights])


def flush_correlation(board):
    """figure out how close the board is to a flush

    Determine how many cards are needed for a flush

    Args:
        board: list of cards in integer form

    Returns:
        integer with the most cards in a possible flush
    """
    board = sorted([x % 4 for x in board])
    return max([board.count(0), board.count(1), \
            board.count(2), board.count(3)])
