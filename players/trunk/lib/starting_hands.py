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
            two_player_percentiles = {
                    (12, 12, False): 1.000000,
                    (11, 11, False): 0.995475,
                    (10, 10, False): 0.990950,
                    (9, 9, False): 0.986425,
                    (8, 8, False): 0.981900,
                    (7, 7, False): 0.977376,
                    (6, 6, False): 0.972851,
                    (11, 12, True): 0.968326,
                    (10, 12, True): 0.965309,
                    (5, 5, False): 0.962293,
                    (9, 12, True): 0.957768,
                    (11, 12, False): 0.954751,
                    (8, 12, True): 0.945701,
                    (10, 12, False): 0.942685,
                    (9, 12, False): 0.933635,
                    (10, 11, True): 0.924585,
                    (7, 12, True): 0.921569,
                    (8, 12, False): 0.918552,
                    (4, 4, False): 0.909502,
                    (9, 11, True): 0.904977,
                    (6, 12, True): 0.901961,
                    (8, 11, True): 0.898944,
                    (5, 12, True): 0.895928,
                    (10, 11, False): 0.892911,
                    (7, 12, False): 0.883861,
                    (3, 12, True): 0.874811,
                    (9, 11, False): 0.871795,
                    (4, 12, True): 0.862745,
                    (9, 10, True): 0.859729,
                    (7, 11, True): 0.856712,
                    (6, 12, False): 0.853695,
                    (3, 3, False): 0.844646,
                    (8, 11, False): 0.840121,
                    (2, 12, True): 0.831071,
                    (8, 10, True): 0.828054,
                    (5, 12, False): 0.825038,
                    (1, 12, True): 0.815988,
                    (6, 11, True): 0.812971,
                    (3, 12, False): 0.809955,
                    (4, 12, False): 0.800905,
                    (9, 10, False): 0.791855,
                    (0, 12, True): 0.782805,
                    (5, 11, True): 0.779789,
                    (7, 11, False): 0.776772,
                    (7, 10, True): 0.767722,
                    (8, 9, True): 0.764706,
                    (2, 12, False): 0.761689,
                    (8, 10, False): 0.752640,
                    (4, 11, True): 0.743590,
                    (1, 12, False): 0.740573,
                    (2, 2, False): 0.731523,
                    (3, 11, True): 0.726998,
                    (6, 10, True): 0.723982,
                    (6, 11, False): 0.720965,
                    (7, 9, True): 0.711916,
                    (5, 11, False): 0.708899,
                    (0, 12, False): 0.699849,
                    (7, 10, False): 0.690799,
                    (2, 11, True): 0.681750,
                    (8, 9, False): 0.678733,
                    (4, 11, False): 0.669683,
                    (5, 10, True): 0.660633,
                    (1, 11, True): 0.657617,
                    (6, 9, True): 0.654600,
                    (7, 8, True): 0.651584,
                    (4, 10, True): 0.648567,
                    (3, 11, False): 0.645551,
                    (6, 10, False): 0.636501,
                    (0, 11, True): 0.627451,
                    (7, 9, False): 0.624434,
                    (3, 10, True): 0.615385,
                    (1, 1, False): 0.612368,
                    (2, 11, False): 0.607843,
                    (6, 8, True): 0.598793,
                    (5, 9, True): 0.595777,
                    (2, 10, True): 0.592760,
                    (5, 10, False): 0.589744,
                    (1, 11, False): 0.580694,
                    (6, 9, False): 0.571644,
                    (7, 8, False): 0.562594,
                    (1, 10, True): 0.553544,
                    (4, 10, False): 0.550528,
                    (6, 7, True): 0.541478,
                    (4, 9, True): 0.538462,
                    (5, 8, True): 0.535445,
                    (0, 11, False): 0.532428,
                    (3, 10, False): 0.523379,
                    (0, 10, True): 0.514329,
                    (3, 9, True): 0.511312,
                    (5, 9, False): 0.508296,
                    (6, 8, False): 0.499246,
                    (2, 10, False): 0.490196,
                    (2, 9, True): 0.481146,
                    (0, 0, False): 0.478130,
                    (5, 7, True): 0.473605,
                    (4, 8, True): 0.470588,
                    (1, 10, False): 0.467572,
                    (1, 9, True): 0.458522,
                    (5, 6, True): 0.455505,
                    (6, 7, False): 0.452489,
                    (5, 8, False): 0.443439,
                    (4, 9, False): 0.434389,
                    (4, 7, True): 0.425339,
                    (0, 9, True): 0.422323,
                    (0, 10, False): 0.419306,
                    (3, 8, True): 0.410256,
                    (3, 9, False): 0.407240,
                    (2, 8, True): 0.398190,
                    (4, 6, True): 0.395173,
                    (2, 9, False): 0.392157,
                    (5, 7, False): 0.383107,
                    (4, 8, False): 0.374057,
                    (3, 7, True): 0.365008,
                    (1, 8, True): 0.361991,
                    (4, 5, True): 0.358974,
                    (1, 9, False): 0.355958,
                    (5, 6, False): 0.346908,
                    (0, 8, True): 0.337858,
                    (3, 6, True): 0.334842,
                    (4, 7, False): 0.331825,
                    (0, 9, False): 0.322775,
                    (3, 8, False): 0.313725,
                    (3, 5, True): 0.304676,
                    (2, 7, True): 0.301659,
                    (2, 8, False): 0.298643,
                    (3, 4, True): 0.289593,
                    (4, 6, False): 0.286576,
                    (1, 7, True): 0.277526,
                    (2, 6, True): 0.274510,
                    (3, 7, False): 0.271493,
                    (1, 8, False): 0.262443,
                    (4, 5, False): 0.253394,
                    (0, 7, True): 0.244344,
                    (2, 5, True): 0.241327,
                    (2, 3, True): 0.238311,
                    (2, 4, True): 0.235294,
                    (0, 8, False): 0.232278,
                    (3, 6, False): 0.223228,
                    (1, 6, True): 0.214178,
                    (3, 5, False): 0.211161,
                    (2, 7, False): 0.202112,
                    (3, 4, False): 0.193062,
                    (0, 6, True): 0.184012,
                    (1, 5, True): 0.180995,
                    (1, 3, True): 0.177979,
                    (1, 7, False): 0.174962,
                    (1, 4, True): 0.165913,
                    (2, 6, False): 0.162896,
                    (0, 7, False): 0.153846,
                    (1, 2, True): 0.144796,
                    (2, 5, False): 0.141780,
                    (2, 3, False): 0.132730,
                    (2, 4, False): 0.123680,
                    (0, 5, True): 0.114630,
                    (0, 3, True): 0.111614,
                    (0, 4, True): 0.108597,
                    (1, 6, False): 0.105581,
                    (0, 2, True): 0.096531,
                    (0, 6, False): 0.093514,
                    (1, 5, False): 0.084465,
                    (1, 3, False): 0.075415,
                    (1, 4, False): 0.066365,
                    (0, 1, True): 0.057315,
                    (1, 2, False): 0.054299,
                    (0, 5, False): 0.045249,
                    (0, 3, False): 0.036199,
                    (0, 4, False): 0.027149,
                    (0, 2, False): 0.018100,
                    (0, 1, False): 0.009050
            }
            return two_player_percentiles[hole]

        if numActivePlayers == 3:
            three_player_percentiles = {
                    (12, 12, False): 1.000000,
                    (11, 11, False): 0.995475,
                    (10, 10, False): 0.990950,
                    (9, 9, False): 0.986425,
                    (8, 8, False): 0.981900,
                    (7, 7, False): 0.977376,
                    (11, 12, True): 0.972851,
                    (10, 12, True): 0.969834,
                    (6, 6, False): 0.966817,
                    (9, 12, True): 0.962293,
                    (11, 12, False): 0.959276,
                    (8, 12, True): 0.950226,
                    (10, 11, True): 0.947210,
                    (10, 12, False): 0.944193,
                    (9, 11, True): 0.935143,
                    (5, 5, False): 0.932127,
                    (9, 12, False): 0.927602,
                    (8, 11, True): 0.918552,
                    (7, 12, True): 0.915535,
                    (8, 12, False): 0.912519,
                    (10, 11, False): 0.903469,
                    (9, 10, True): 0.894419,
                    (6, 12, True): 0.891403,
                    (8, 10, True): 0.888386,
                    (9, 11, False): 0.885370,
                    (5, 12, True): 0.876320,
                    (7, 11, True): 0.873303,
                    (4, 4, False): 0.870287,
                    (3, 12, True): 0.865762,
                    (8, 9, True): 0.862745,
                    (8, 11, False): 0.859729,
                    (7, 12, False): 0.850679,
                    (4, 12, True): 0.841629,
                    (9, 10, False): 0.838612,
                    (2, 12, True): 0.829563,
                    (6, 12, False): 0.826546,
                    (7, 10, True): 0.817496,
                    (6, 11, True): 0.814480,
                    (1, 12, True): 0.811463,
                    (8, 10, False): 0.808446,
                    (5, 12, False): 0.799397,
                    (5, 11, True): 0.790347,
                    (7, 9, True): 0.787330,
                    (0, 12, True): 0.784314,
                    (7, 11, False): 0.781297,
                    (3, 3, False): 0.772247,
                    (8, 9, False): 0.767722,
                    (3, 12, False): 0.758673,
                    (7, 8, True): 0.749623,
                    (4, 11, True): 0.746606,
                    (6, 10, True): 0.743590,
                    (4, 12, False): 0.740573,
                    (3, 11, True): 0.731523,
                    (2, 12, False): 0.728507,
                    (7, 10, False): 0.719457,
                    (6, 9, True): 0.710407,
                    (6, 11, False): 0.707391,
                    (2, 11, True): 0.698341,
                    (1, 12, False): 0.695324,
                    (6, 8, True): 0.686275,
                    (5, 10, True): 0.683258,
                    (7, 9, False): 0.680241,
                    (5, 11, False): 0.671192,
                    (1, 11, True): 0.662142,
                    (6, 7, True): 0.659125,
                    (4, 10, True): 0.656109,
                    (0, 12, False): 0.653092,
                    (2, 2, False): 0.644042,
                    (7, 8, False): 0.639517,
                    (5, 9, True): 0.630468,
                    (6, 10, False): 0.627451,
                    (4, 11, False): 0.618401,
                    (0, 11, True): 0.609351,
                    (3, 10, True): 0.606335,
                    (5, 8, True): 0.603318,
                    (3, 11, False): 0.600302,
                    (2, 10, True): 0.591252,
                    (5, 7, True): 0.588235,
                    (6, 9, False): 0.585219,
                    (5, 6, True): 0.576169,
                    (4, 9, True): 0.573152,
                    (6, 8, False): 0.570136,
                    (1, 10, True): 0.561086,
                    (2, 11, False): 0.558069,
                    (5, 10, False): 0.549020,
                    (3, 9, True): 0.539970,
                    (4, 8, True): 0.536953,
                    (6, 7, False): 0.533937,
                    (0, 10, True): 0.524887,
                    (1, 1, False): 0.521870,
                    (4, 10, False): 0.517345,
                    (1, 11, False): 0.508296,
                    (4, 7, True): 0.499246,
                    (2, 9, True): 0.496229,
                    (4, 6, True): 0.493213,
                    (5, 9, False): 0.490196,
                    (4, 5, True): 0.481146,
                    (3, 10, False): 0.478130,
                    (0, 11, False): 0.469080,
                    (5, 8, False): 0.460030,
                    (1, 9, True): 0.450980,
                    (3, 8, True): 0.447964,
                    (5, 7, False): 0.444947,
                    (2, 10, False): 0.435897,
                    (0, 9, True): 0.426848,
                    (5, 6, False): 0.423831,
                    (3, 7, True): 0.414781,
                    (3, 4, True): 0.411765,
                    (2, 8, True): 0.408748,
                    (3, 5, True): 0.405732,
                    (3, 6, True): 0.402715,
                    (4, 9, False): 0.399698,
                    (1, 10, False): 0.390649,
                    (1, 8, True): 0.381599,
                    (0, 0, False): 0.378582,
                    (3, 9, False): 0.374057,
                    (4, 8, False): 0.365008,
                    (2, 3, True): 0.355958,
                    (0, 10, False): 0.352941,
                    (0, 8, True): 0.343891,
                    (4, 7, False): 0.340875,
                    (2, 4, True): 0.331825,
                    (4, 6, False): 0.328808,
                    (4, 5, False): 0.319759,
                    (2, 7, True): 0.310709,
                    (2, 9, False): 0.307692,
                    (2, 5, True): 0.298643,
                    (2, 6, True): 0.295626,
                    (1, 7, True): 0.292609,
                    (1, 9, False): 0.289593,
                    (3, 8, False): 0.280543,
                    (1, 3, True): 0.271493,
                    (0, 7, True): 0.268477,
                    (3, 4, False): 0.265460,
                    (3, 7, False): 0.256410,
                    (0, 9, False): 0.247360,
                    (1, 4, True): 0.238311,
                    (3, 5, False): 0.235294,
                    (2, 8, False): 0.226244,
                    (3, 6, False): 0.217195,
                    (1, 5, True): 0.208145,
                    (1, 6, True): 0.205128,
                    (1, 2, True): 0.202112,
                    (0, 6, True): 0.199095,
                    (1, 8, False): 0.196078,
                    (2, 3, False): 0.187029,
                    (0, 3, True): 0.177979,
                    (2, 4, False): 0.174962,
                    (0, 8, False): 0.165913,
                    (0, 4, True): 0.156863,
                    (2, 7, False): 0.153846,
                    (2, 5, False): 0.144796,
                    (0, 2, True): 0.135747,
                    (0, 5, True): 0.132730,
                    (2, 6, False): 0.129713,
                    (1, 7, False): 0.120664,
                    (0, 1, True): 0.111614,
                    (1, 3, False): 0.108597,
                    (0, 7, False): 0.099548,
                    (1, 4, False): 0.090498,
                    (1, 2, False): 0.081448,
                    (1, 5, False): 0.072398,
                    (1, 6, False): 0.063348,
                    (0, 6, False): 0.054299,
                    (0, 3, False): 0.045249,
                    (0, 4, False): 0.036199,
                    (0, 2, False): 0.027149,
                    (0, 5, False): 0.018100,
                    (0, 1, False): 0.009050
            }
            return three_player_percentiles[hole]
