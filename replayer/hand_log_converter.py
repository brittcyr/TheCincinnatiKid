import datetime
import os

class Printer(object):
    results = ''
    tourney_num = int(datetime.datetime.now().strftime("%s")) * 10000
    hand_num = int(datetime.datetime.now().strftime("%s")) * 10000
    player_three_in = True
    loser = ''
    second = ''
    winner = ''
    filename = ''
    @classmethod
    def reset(cls):
        cls.results = ''
        cls.loser = ''
        cls.second = ''
        cls.winner = ''
        cls.filename = ''

    @classmethod
    def add_hand(cls, hand):
        cls.results += hand

    @classmethod
    def write_result(cls):
        cls.tourney_in_round += 1
        file_name = cls.file_name + str(cls.tourney_in_round)
        f = open(file_name, 'w')
        f.write(cls.results)
        f.write("Pokerstars Tournament #%d, Pot Limit Hold'em\n" % cls.tourney_num)
        f.write("Buy-In: 80/0\n")
        f.write("3 players\n")
        f.write("Total Prize Pool: 240\n")
        f.write("1: %s , 180\n" % cls.winner)
        f.write("2: %s , 60\n" % cls.second)
        f.write("3: %s \n" % cls.loser)
        f.close()

def create_new_game_line(game_num, tournament_num):
    return "Pokerstars Game #%d: Tournament #%d, Hold'em Pot Limit ($1/$2) - %s\n" % (Printer.hand_num, tournament_num, datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S ET"))

def table():
    return "Table '1' 3-max Seat #1 is the button\n"

def seats(p1name, p1val, p2name, p2val, p3name, p3val):
    seat1 = "Seat 1: %s (%d in chips)" % (p1name, p1val)
    seat2 = "Seat 2: %s (%d in chips)" % (p2name, p2val)
    seats = seat1 + '\n' + seat2 + '\n'
    if Printer.player_three_in:
        seat3 = "Seat 3: %s (%d in chips)" % (p3name, p3val)
        return seats + seat3 + '\n'
    else:
        Printer.loser = p3name
        return seats

def blinds(sb, bb):
    small = '%s: posts small blind 1\n' % (sb)
    big = '%s: posts big blind 2\n' % (bb)
    return small + big

def hole(hole_cards, hero):
    dealt = 'Dealt to %s [%s %s]\n' % (hero, hole_cards[0], hole_cards[1])
    return dealt

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
        return action
    if ' checks' in action_line:
        action = 'CHECK:%s' % (player)
        return action
    if ' bets ' in action_line:
        action = 'BET:%s:%s' % (action_line.split()[-1], player)
        return action
    if ' raises ' in action_line:
        action = 'RAISE:%s:%s' % (action_line.split()[-1], player)
        return action
    if ' fold' in action_line:
        action = 'FOLD:%s' % (player)
        return action
    if ' returned ' in action_line:
        return ''
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


def parse_file(filename, hero):
    f = open(filename, 'r')
    prev_actions = []

    for line in f:
        line = line.strip()
        if 'Hand #' in line:
            if prev_actions:
                do_print(p1name, p1val, p2name, p2val, p3name, p3val, hero, prev_actions, hero_hole, hand_num, final_pot, board, holes)
                final_pot = 0
            hero_hole = []
            final_pot = 0
            prev_actions = []
            pot = 0
            numBoardCards = 0
            board = []
            numActive = 2
            holes = {}
            p1name, p1val, p2name, p2val, p3name, p3val = parse_hand_line(line)
            showdown = False
            hand_num = int(line.split('#')[1].split(',')[0])

            if all([p1name, p2name, p3name]):
                numActive = 3

            if int(p3val) == 0:
                Printer.player_three_in = False
                pot_round = {p1name: 1, p2name: 2}
            else:
                Printer.player_three_in = True
                pot_round = {p2name: 1, p3name: 2}

            if p1name == hero: seat = 1
            elif p2name == hero: seat = 2
            else: seat = 3
            pot_round[p1name] = 0
            pot_round[p2name] = 0
            pot_round[p3name] = 0

        if ' posts ' in line:
            blind_action = parse_blind_line(line)
            pot_round[blind_action.split(':')[-1]] += int(blind_action.split(':')[1])
            prev_actions.append(blind_action)
        if 'Dealt to ' in line:
            dealt_to, card1, card2 = parse_hole_line(line)
            if hero in dealt_to:
                hero_hole = [card1, card2]
            holes[dealt_to] = (card1, card2)

        if 'calls' in line or 'raises' in line or 'checks' in line or 'folds' in line or 'bet' in line:
            action = parse_action_line(line)
            if not action: continue
            if hero == action.split(':')[-1]:
                potsize = sum(pot_round.values()) + pot

            if 'raise' in line or 'bet' in line or 'call' in line:
                old_action = action
                pot_action, amount, player = action.split(':')
                if pot_action == 'RAISE':
                    action = '%s: raises to %s' % (player, amount)
                if pot_action == 'BET':
                    action = '%s: bets %s' % (player, amount)
                if pot_action == 'CALL':
                    amount = int(amount)
                    action = '%s: calls %d' % (player, amount - int(pot_round[action.split(':')[-1]]))

                pot_round[old_action.split(':')[-1]] = int(old_action.split(':')[1])

            if 'FOLD' in action:
                action, player = action.split(':')
                action = '%s: folds' % (player.strip())

            if 'CHECK' in action:
                action, player = action.split(':')
                action = '%s: checks' % (player.strip())

            prev_actions.append(action)

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

            if 'FLOP' in action:
                action = '*** FLOP *** [%s %s %s]' % (cards[0], cards[1], cards[2])
            if 'TURN' in action:
                action = '*** TURN *** [%s %s %s] [%s]' % (board[0], board[1], board[2], cards[0])
            if 'RIVER' in action:
                action = '*** RIVER *** [%s %s %s %s] [%s]' % (board[0], board[1], board[2], board[3], cards[0])
            prev_actions.append(action)
            board += cards

        if 'shows' in line:
            if not showdown:
                prev_actions.append('*** SHOW DOWN ***')
                showdown = True

            player, hand = line.split(' shows ')
            hole1, hole2 = hand.replace('[', '').replace(']', '').split()
            action = '%s: shows [%s %s]' % (player, hole1, hole2)
            prev_actions.append(action)

        if 'wins' in line:
            winner = line.split('wins')[0].split()[0]
            final_pot = int(line.split('(')[1].split(')')[0])

            pot_round_vals = sorted(pot_round.values())
            if pot_round_vals[-1] != pot_round_vals[-2]:
                final_pot -= pot_round_vals[-1]
                final_pot += pot_round_vals[-2]
            prev_actions.append('%s collected %d from the pot' % (winner, final_pot))
            if winner == p1name:
                Printer.winner = winner
                Printer.second = p2name
            if winner == p2name:
                Printer.winner = winner
                Printer.second = p1name

        if 'ties' in line:
            player = line.split('ties')[0].split()[0]
            take = int(line.split('(')[1].split(')')[0])
            prev_actions.append('%s collected %d from the pot' % (player, take))
            final_pot += take

        if 'illegal' in line.lower():
            continue

        if '6.176 MIT Pokerbots ' in line:
            if Printer.winner:
                do_print(p1name, p1val, p2name, p2val, p3name, p3val, hero, prev_actions, hero_hole, hand_num, final_pot, board, holes)
            else:
                continue

    f.close()
    do_print(p1name, p1val, p2name, p2val, p3name, p3val, hero, prev_actions, hero_hole, hand_num, final_pot, board, holes)


def do_print(p1name, p1val, p2name, p2val, p3name, p3val, hero, prev_actions, hero_hole, hand_num, pot_size, board, holes):
    hand_str = create_new_game_line(hand_num, Printer.tourney_num)
    hand_str += table()
    hand_str += seats(p1name, p1val, p2name, p2val, p3name, p3val)
    if int(p3val) == 0:
        hand_str += blinds(p1name, p2name)
    else:
        hand_str += blinds(p2name, p3name)

    hand_str += '*** HOLE CARDS ***\n'
    for hole_player in holes:
        if (hole_player == p3name and Printer.player_three_in) or hole_player != p3name:
            hand_str += hole(holes[hole_player], hole_player)

    for action in prev_actions:
        if 'POST' in action: continue
        hand_str += action + '\n'
    hand_str += "*** SUMMARY ***\n"
    hand_str += "Total pot $%d | Rake $0\n" % (pot_size)
    if board:
        if len(board) == 3:
            hand_str += "Board [%s %s %s]\n" % (board[0], board[1], board[2])
        if len(board) == 4:
            hand_str += "Board [%s %s %s %s]\n" % (board[0], board[1], board[2], board[3])
        if len(board) == 5:
            hand_str += "Board [%s %s %s %s %s]\n" % (board[0], board[1], board[2], board[3], board[4])
    hand_str += "Seat 1: %s (button)\n" % (p1name)
    hand_str += "Seat 2: %s (small blind)\n" % (p2name)
    if int(p3val) > 0:
        hand_str += "Seat 3: %s (big blind)\n" % (p3name)
    #else:
    #    hand_str += "Seat 3: %s\n" % (p3name)

    hand_str += '\n'
    Printer.add_hand(hand_str)
    Printer.hand_num += 1

if __name__ == '__main__':
    prefix = '../hand_logs/Day8/'
    files = os.listdir(prefix)
    for filename in files:
        Printer.reset()
        Printer.filename = filename
        Printer.tourney_in_round = 0
        parse_file(prefix + filename, 'TheCincinnatiKid')
        results_prefix = './results/'
        Printer.write_result()
        Printer.tourney_num += 1
