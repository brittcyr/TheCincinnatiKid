from random import shuffle
from hand_eval import get_best_five, eval_hand


# This classifies all the hole cards
def classify_hole(hole_card1, hole_card2):
    hole_cards = [hole_card1, hole_card2]
    suited = hole_cards[0] % 4 == hole_cards[1] % 4
    vals = sorted([x % 13 for x in hole_cards])
    vals = vals + [suited]

    return tuple(vals)


if __name__ == '__main__':
    wins = {}
    losses = {}

    for _ in range(10000000):
        deck = range(52)
        shuffle(deck)

        first = classify_hole(deck[0], deck[1])
        second = classify_hole(deck[2], deck[3])

        if first not in wins:
            wins[first] = 0
            losses[first] = 0
        if second not in wins:
            wins[second] = 0
            losses[second] = 0

        first_hand = [deck[0], deck[1], deck[4], deck[5], deck[6], deck[7], deck[8]]
        second_hand = [deck[2], deck[3], deck[4], deck[5], deck[6], deck[7], deck[8]]

        first_hand = get_best_five(first_hand)
        second_hand = get_best_five(second_hand)

        if eval_hand(first_hand) > eval_hand(second_hand):
            wins[first] += 1
            losses[second] += 1
        else:
            wins[second] += 1
            losses[first] += 1

        if _ % 10000 == 0:
            print 'Complete %d iterations' % (_)
            f = open('two_handed_results.csv', 'w')
            for start in wins:
                f.write('%s,%d,%d,%f\n' % (str(start), wins[start], losses[start], \
                        float(wins[start]) / float(wins[start] + losses[start])))
            f.close()


    wins = {}
    losses = {}
    for _ in range(100000000):
        deck = range(52)
        shuffle(deck)

        first = classify_hole(deck[0], deck[1])
        second = classify_hole(deck[2], deck[3])
        third = classify_hole(deck[4], deck[5])

        if first not in wins:
            wins[first] = 0
            losses[first] = 0
        if second not in wins:
            wins[second] = 0
            losses[second] = 0
        if third not in wins:
            wins[third] = 0
            losses[third] = 0

        first_hand = [deck[0], deck[1], deck[6], deck[7], deck[8], deck[9], deck[10]]
        second_hand = [deck[2], deck[3], deck[6], deck[7], deck[8], deck[9], deck[10]]
        third_hand = [deck[4], deck[5], deck[6], deck[7], deck[8], deck[9], deck[10]]

        first_hand = get_best_five(first_hand)
        second_hand = get_best_five(second_hand)
        third_hand = get_best_five(third_hand)

        if eval_hand(first_hand) > eval_hand(second_hand):
            if eval_hand(first_hand) > eval_hand(third_hand):
                wins[first] += 1
                losses[second] += 1
                losses[third] += 1
            else:
                losses[first] += 1
                losses[second] += 1
                wins[third] += 1
        else:
            if eval_hand(second_hand) > eval_hand(third_hand):
                losses[first] += 1
                wins[second] += 1
                losses[third] += 1
            else:
                losses[first] += 1
                losses[second] += 1
                wins[third] += 1


        if _ % 10000 == 0:
            print 'Complete %d iterations' % (_)
            f = open('three_handed_results.csv', 'w')
            for start in wins:
                f.write('%s,%d,%d,%f\n' % (str(start), wins[start], losses[start], \
                        float(wins[start]) / float(wins[start] + losses[start])))
            f.close()


class HoleScorer(object):
    @classmethod
    def score_hole(self, hole, numActivePlayers):
        if numActivePlayers == 2:
            two_player_percentiles = {}
            f = open('lib/two_handed_results.csv', 'r')
            for line in f:
                line = line.strip()
                [lo, hi, suited, percentile] = line.split(',')
                lo = int(lo.replace('(', ''))
                hi = int(hi)
                percent = float(percentile)
                suited = 'T' in suited.replace(')', '')
                two_player_percentiles[(lo, hi, suited)] = percent
            f.close()

            return two_player_percentiles[hole]

        if numActivePlayers == 3:
            three_player_percentiles = {}
            f = open('lib/three_handed_results.csv', 'r')
            for line in f:
                line = line.strip()
                [lo, hi, suited, percentile] = line.split(',')
                lo = int(lo.replace('(', ''))
                hi = int(hi)
                percent = float(percentile)
                suited = 'T' in suited.replace(')', '')
                three_player_percentiles[(lo, hi, suited)] = percent
            f.close()

            return three_player_percentiles[hole]
