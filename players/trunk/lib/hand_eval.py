"""
A hand score will be a tuple
0 = high card
1 = one pair
2 = two pair
3 = three of a kind
4 = straight
5 = flush               Cards in order
6 = full house          Three, two
7 = four of a kind      High card
8 = straight flush      4 then other card
9 = royal flush         No kicker
"""

def convert_int_to_string(card):
    """convert a card to string form

    Args:
        card: A card in int form

    Returns:
        card in string form
    """
    cards = {0 : '2s', 1 : '2h', 2 : '2d', 3 : '2c', 4 : '3s', 5 : '3h',
             6 : '3d', 7 : '3c', 8 : '4s', 9 : '4h', 10 : '4d', 11 : '4c',
             12 : '5s', 13 : '5h', 14 : '5d', 15 : '5c', 16 : '6s', 17 : '6h',
             18 : '6d', 19 : '6c', 20 : '7s', 21 : '7h', 22 : '7d', 23 : '7c',
             24 : '8s', 25 : '8h', 26 : '8d', 27 : '8c', 28 : '9s', 29 : '9h',
             30 : '9d', 31 : '9c', 32 : 'Ts', 33 : 'Th', 34 : 'Td', 35 : 'Tc',
             36 : 'Js', 37 : 'Jh', 38 : 'Jd', 39 : 'Jc', 40 : 'Qs', 41 : 'Qh',
             42 : 'Qd', 43 : 'Qc', 44 : 'Ks', 45 : 'Kh', 46 : 'Kd', 47 : 'Kc',
             48 : 'As', 49 : 'Ah', 50 : 'Ad', 51 : 'Ac'}

    return cards[card]

def convert_string_to_int(card):
    """convert a card to int form

    Args:
        card: A card in string form

    Returns:
        card in int form
    """
    cards = {'2s' : 0, '2h' : 1, '2d' : 2, '2c' : 3, '3s' : 4, '3h' : 5,
             '3d' : 6, '3c' : 7, '4s' : 8, '4h' : 9, '4d' : 10, '4c' : 11,
             '5s' : 12, '5h' : 13, '5d' : 14, '5c' : 15, '6s' : 16, '6h' : 17,
             '6d' : 18, '6c' : 19, '7s' : 20, '7h' : 21, '7d' : 22, '7c' : 23,
             '8s' : 24, '8h' : 25, '8d' : 26, '8c' : 27, '9s' : 28, '9h' : 29,
             '9d' : 30, '9c' : 31, 'Ts' : 32, 'Th' : 33, 'Td' : 34, 'Tc' : 35,
             'Js' : 36, 'Jh' : 37, 'Jd' : 38, 'Jc' : 39, 'Qs' : 40, 'Qh' : 41,
             'Qd' : 42, 'Qc' : 43, 'Ks' : 44, 'Kh' : 45, 'Kd' : 46, 'Kc' : 47,
             'As' : 48, 'Ah' : 49, 'Ad' : 50, 'Ac' : 51}

    return cards[card]

def is_straight(hand):
    """check if there is a straight in the hand

    Args:
        hand: A sorted list of cards in int form

    Returns:
        boolean whether it is a straight
    """
    hand = sorted([card / 4 for card in hand])
    # Check first three connections
    for count in xrange(3):
        if hand[count] + 1 != hand[count + 1]:
            return False

    final = hand[-1]
    # Consider possibility of a wheel
    if final == 12:
        if hand[3] == 11 or hand[0] == 0:
            return True
        else:
            return False

    # Check last connection
    if hand[-1] != hand[-2] + 1:
        return False

    return True

def is_flush(hand):
    """check if there is a flush in the hand

    Args:
        hand: A sorted list of cards in int form

    Returns:
        boolean whether it is a flush
    """
    hand = [card % 4 for card in hand]
    return all([hand[count] == hand[0] for count in range(len(hand))])

def is_royal_flush(hand):
    """check if there is a royal flush in the hand

    Args:
        hand: A sorted list of cards in int form

    Returns:
        boolean whether it is a royal flush
    """
    return hand[-2] >= 44 and is_straight_flush(hand)

def is_straight_flush(hand):
    """check if there is a straight flush in the hand

    Args:
        hand: A sorted list of cards in int form

    Returns:
        boolean whether it is a straight flush
    """
    return is_flush(hand) and is_straight(hand)

def is_four_of_a_kind(hand):
    """check if there is a four of a kind in the hand

    Args:
        hand: A sorted list of cards in int form

    Returns:
        boolean whether it is a four of a kind
    """
    if hand[1] + 1 == hand[2] and hand[2] + 1 == hand[3]:
        if hand[0] + 1 == hand[1] or hand[3] == hand[4]:
            return True
    return False

def is_full_house(hand):
    """check if there is a full house in the hand

    Args:
        hand: A sorted list of cards in int form

    Returns:
        boolean whether it is a full house
    """
    hand = [card / 4 for card in hand]
    hand.sort()
    if hand[0] == hand[1] and hand[3] == hand[4]:
        if hand[2] == hand[1] or hand[2] == hand[3]:
            return True
    return False

def is_three_of_a_kind(hand):
    """check if there is a three of a kind in the hand

    Args:
        hand: A sorted list of cards in int form

    Returns:
        boolean whether it is a three of a kind
    """
    hand = [card / 4 for card in hand]
    if hand[0] == hand[1] and hand[1] == hand[2]:
        return True
    if hand[1] == hand[2] and hand[2] == hand[3]:
        return True
    if hand[2] == hand[3] and hand[3] == hand[4]:
        return True
    return False

def is_two_pair(hand):
    """check if there is two pair in the hand

    Args:
        hand: A sorted list of cards in int form

    Returns:
        boolean whether it is two pair
    """
    hand = [card / 4 for card in hand]
    hand.sort()
    if hand[0] == hand[1]:
        return hand[2] == hand[3] or hand[3] == hand[4]
    if hand[3] == hand[4]:
        return hand[0] == hand[1] or hand[1] == hand[2]
    return False

def is_pair(hand):
    """check if there is a pair in the hand

    Args:
        hand: A sorted list of cards in int form

    Returns:
        boolean whether it is a pair
    """
    hand = [card / 4 for card in hand]
    for first in range(4):
        for second in range(first + 1, 5):
            if hand[first] == hand[second]:
                return True
    return False

def eval_hand(hand):
    """score the hand using tuples that when sorted order hands

    Args:
        hand: A sorted list of cards in int form

    Returns:
        tuple with the first index being type of hand and others are kickers
    """
    hand.sort()

    if is_royal_flush(hand):
        return (9,)

    if is_straight_flush(hand):
        hand = [card / 4 for card in hand]
        return (8, hand[4])

    if is_four_of_a_kind(hand):
        hand = [card / 4 for card in hand]
        if hand[0] == hand[1]:
            return (7, hand[0] / 4, hand[4])
        return (7, hand[4] / 4, hand[0])

    if is_full_house(hand):
        hand = [card / 4 for card in hand]
        if hand[2] == hand[0]:
            return (6, hand[2], hand[4])
        return (6, hand[2], hand[0])

    if is_flush(hand):
        hand = [card / 4 for card in hand]
        hand.reverse()
        return (5, hand)

    if is_straight(hand):
        hand = [card / 4 for card in hand]
        if hand[0] == 0 and hand[4] == 12:
            return (4, 4)
        return (4, hand[4])

    if is_three_of_a_kind(hand):
        hand = [card / 4 for card in hand]
        if hand[0] == hand[2]:
            return (3, hand[2], hand[4], hand[3])
        if hand[1] == hand[3]:
            return (3, hand[2], hand[4], hand[0])
        if hand[2] == hand[4]:
            return (3, hand[2], hand[1], hand[0])

    if is_two_pair(hand):
        hand = [card / 4 for card in hand]
        if hand[0] != hand[1]:
            return (2, hand[4], hand[2], hand[0])
        if hand[1] != hand[2] and hand[2] != hand[3]:
            return (2, hand[4], hand[1], hand[2])
        if hand[3] != hand[4]:
            return (2, hand[3], hand[1], hand[4])

    if is_pair(hand):
        hand = [card / 4 for card in hand]
        if hand[0] == hand[1]:
            return (1, hand[0], hand[4], hand[3], hand[2])
        if hand[1] == hand[2]:
            return (1, hand[1], hand[4], hand[3], hand[0])
        if hand[2] == hand[3]:
            return (1, hand[2], hand[4], hand[1], hand[0])
        if hand[3] == hand[4]:
            return (1, hand[3], hand[2], hand[1], hand[0])

    hand.reverse()
    return (0, hand)

def get_best_five(cards):
    """make the best five card hand

    Args:
        hand: A sorted list of cards in int form

    Returns:
        list of best five card poker hand
    """
    cards.sort()

    if len(cards) == 5:
        return cards

    best = (0, cards)

    if len(cards) == 6:
        for missing in range(6):
            current = [cards[x] for x in range(6) if x != missing]
            score = eval_hand(current)
            if score > best[0]:
                best = (score, current)
        return best[1]

    if len(cards) == 7:
        for missing1 in range(6):
            for missing2 in range(missing1 + 1, 7):
                current = [cards[x] for x in range(7)  \
                        if x != missing1 and x != missing2]
                score = eval_hand(current)
                if score > best[0]:
                    best = (score, current)
        return best[1]

def score_best_five(cards):
    """make the best five card hand

    Args:
        hand: A sorted list of cards in int form

    Returns:
        the score of the best hand
    """
    cards.sort()

    if len(cards) == 5:
        return eval_hand(cards)

    best = (0, cards)

    if len(cards) == 6:
        for missing in range(6):
            current = [cards[x] for x in range(6) if x != missing]
            score = eval_hand(current)
            if score > best[0]:
                best = (score, current)
        return best[0]

    if len(cards) == 7:
        for missing1 in range(6):
            for missing2 in range(missing1 + 1, 7):
                current = [cards[x] for x in range(7)  \
                        if x != missing1 and x != missing2]
                score = eval_hand(current)
                if score > best[0]:
                    best = (score, current)
        return best[0]
