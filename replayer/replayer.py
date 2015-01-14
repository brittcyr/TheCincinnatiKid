import argparse


def create_new_game_line(p1name, p1val, p2name, p2val, p3name, p3val):
    return "NEWGAME %s %s %s 200 2 1000 10.000000" % (p1name, p2name, p3name)

def create_new_hand_line(p1name, p1val, p2name, p2val, p3name, p3val, hole1, hole2, seat):
    # NEWHAND handId seat holeCard1 holeCard2 [stackSizes] [playerNames] numActivePlayers [activePlayers] timeBank
    active = 2
    if all([p1name, p2name, p3name]):
        active = 3
    return "NEWHAND 1 %s %s %s %d %d %d %s %s %s %d true true true 10.000000" % \
            (seat, hole1, hole2, p1val, p2val, p3val, p1name, p2name, p3name, active)


# For now, assume that we are seat one
def parse_file(filename, hero):
    hero_hole = []
    f = open(filename, 'r')
    results = []

    prev_actions = []
    pot_round = {}
    pot = 0
    numBoardCards = 0
    board = []
    numActive = 2
    getactions = []

    for line in f:
        line = line.strip()
        if 'Hand #' in line:
            p1name, p1val, p2name, p2val, p3name, p3val = parse_hand_line(line)

            if all([p1name, p2name, p3name]):
                numActive = 3

            if p1name == hero:
                seat = 1
            elif p2name == hero:
                seat = 2
            else:
                seat = 3
            pot_round[p1name] = 0
            pot_round[p2name] = 0
            pot_round[p3name] = 0

        if ' posts ' in line:
            blind_action = parse_blind_line(line)
            pot_round[blind_action.split(':')[-1]] += int(blind_action.split(':')[1])
            prev_actions.append(blind_action)
        if 'Dealt to ' in line:
            dealt_to, card1, card2 = parse_hole_line(line)
            if dealt_to == hero:
                hero_hole = [card1, card2]

        if 'calls' in line or 'raises' in line or 'checks' in line or 'folds' in line or 'bet' in line:
            action = parse_action_line(line)
            if hero == action.split(':')[-1]:
                getaction = "GETACTION "
                potsize = sum(pot_round.values()) + pot

                legal = []
                bets = [x for x in prev_actions if ('RAISE' in x or 'BET' in x or 'POST:2' in x) and hero != x.split(':')[-1]]
                if bets:
                    legal.append('FOLD')
                    last_bet = bets[-1]
                    legal.append('CALL:%s' % (last_bet.split(':')[1]))
                    minbet = int(last_bet.split(':')[1]) + pot_round[hero] # TODO: this is wrong when 3 players betting
                    amount_to_raise_to = potsize + pot_round[hero]
                    legal.append('RAISE:%d:%d' % (minbet, amount_to_raise_to))
                else:
                    legal.append('CHECK')
                    amount_to_raise_to = potsize + pot_round[hero]
                    if [x for x in prev_actions if 'POST' in x]:
                        legal.append('RAISE:4:%d' % (amount_to_raise_to))
                    else:
                        legal.append('BET:2:%d' % (amount_to_raise_to))

                # GETACTION potSize numBoardCards [boardCards] [stackSizes] numActivePlayers [activePlayers] numLastActions [lastActions] numLegalActions [legalActions] timebank

                getaction += '%d %d' % (potsize, numBoardCards)
                for card in board:
                    getaction += ' '
                    getaction += card

                getaction += ' 0 0 0'
                getaction += ' ' + str(numActive)

                getaction += ' true true true'

                getaction += ' ' + str(len(prev_actions))
                for action in prev_actions:
                    getaction += ' ' + action

                getaction += ' ' + str(len(legal))
                for action in legal:
                    getaction += ' ' + action

                getaction += ' 10.0'
                getactions.append(getaction)


                prev_actions = []

            prev_actions.append(action)

            if 'raise' in line or 'bet' in line or 'call' in line:
                pot_round[action.split(':')[-1]] = int(action.split(':')[1])

        if '***' in line:
            action, cards = parse_deal_line(line)
            pot += pot_round[p1name]
            pot += pot_round[p2name]
            pot += pot_round[p3name]
            pot_round[p1name] = 0
            pot_round[p2name] = 0
            pot_round[p3name] = 0
            if 'FLOP' in action:
                numBoardCards += 3
            else:
                numBoardCards += 1
            prev_actions.append(action)
            board += cards


        if 'shows' in line:
            continue
        if 'wins' in line:
            continue

    f.close()
    results.insert(0, create_new_hand_line(p1name, p1val, p2name, p2val, p3name, p3val, hero_hole[0], hero_hole[1], seat))
    results.insert(0, create_new_game_line(p1name, p1val, p2name, p2val, p3name, p3val))
    results += getactions
    f = open('actions', 'w')
    for action in results:
        print action
        f.write('%s\n' % (action))
    f.close()


def parse_hand_line(hand_line):
    # First get the names
    [h, p1, p2, p3] = hand_line.split(',')
    p1name, p1val = p1.replace(')', '').split('(')
    p2name, p2val = p2.replace(')', '').split('(')
    p3name, p3val = p3.replace(')', '').split('(')
    p1name = p1name.strip()
    p2name = p2name.strip()
    p3name = p3name.strip()
    p1val = int(p1val)
    p2val = int(p2val)
    p3val = int(p3val)
    return p1name, p1val, p2name, p2val, p3name, p3val


def parse_blind_line(blind_line):
    poster = blind_line.split()[0].strip()
    blind = int(blind_line.split()[-1].strip())
    blind_action = 'POST:%d:%s' % (blind, poster)
    return blind_action


def parse_hole_line(deal_line):
    dealt_to = deal_line.split('Dealt to ')[-1].split()[0].strip()
    card1 = deal_line.split('[')[-1].split()[0]
    card2 = deal_line.split('[')[-1].split(']')[0].split()[1]
    return dealt_to, card1, card2

def parse_action_line(action_line):
    player = action_line.split()[0]
    # Possible actions are BET CALL CHECK FOLD RAISE DEAL
    if ' calls ' in action_line:
        action = 'CALL:%s:%s' % (action_line.split()[-1], player)
    if ' checks' in action_line:
        action = 'CHECK:%s' % (player)
    if ' bets ' in action_line:
        action = 'BET:%s:%s' % (action_line.split()[-1], player)
    if ' raises ' in action_line:
        action = 'RAISE:%s:%s' % (action_line.split()[-1], player)
    if ' fold' in action_line:
        action = 'FOLD:%s' % (player)
    return action


def parse_deal_line(deal_line):
    if 'FLOP' in deal_line:
        street = deal_line.split('***')[1].strip()
        action = 'DEAL:%s' % (street)
        card1 = deal_line.split('[')[-1].split()[0]
        card2 = deal_line.split('[')[-1].split(']')[0].split()[1]
        card3 = deal_line.split('[')[-1].split(']')[0].split()[2]
        cards = [card1, card2, card3]
    else:
        street = deal_line.split('***')[1].strip()
        action = 'DEAL:%s' % (street)
        cards = [deal_line.split('[')[-1].split()[0]]
        cards = [x.replace(']', '') for x in cards]
    return action, cards

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GETACTION reconstructor.', add_help=False, prog='pokerbot')
    parser.add_argument('-h', dest='hero', type=str, default='DTREE', help='HERO name')
    args = parser.parse_args()
    parse_file('hand', args.hero)
