import subprocess
import argparse
import os
import os.path
import shutil
import random
import math
from datetime import datetime


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run tournament.', add_help=False, prog='pokerbot')
    parser.add_argument('-t', dest='times', type=int, default=1, help='Times to run')
    args = parser.parse_args()
    start_time = datetime.now()

    dirs = []

    scores = {}
    wins = {}
    seconds = {}
    lasts = {}

    for iteration in xrange(args.times):
        new_dirs = [x for x in os.listdir("players") if os.path.isdir("players/" + x)]
        if new_dirs != dirs:
            dirs = new_dirs
            if 'RANDOM' not in scores:
                scores = {'RANDOM': 0}
                wins = {'RANDOM': 0}
                seconds = {'RANDOM': 0}
                lasts = {'RANDOM': 0}
	    for d in dirs:
                if d not in scores:
                    scores[d] = 0
                    wins[d] = 0
                    seconds[d] = 0
                    lasts[d] = 0

        config = open("config.txt", "w")
        config.write("BIG_BLIND = 2\nSTARTING_STACK = 200\nNUMBER_OF_HANDS = 1000\n")
        config.write("CONNECTION_TIMEOUT = 5\nTIME_RESTRICTION_PER_GAME = 100\n")
        config.write("ENFORCE_TIMING_RESTRICTION = true\nDISPLAY_ILLEGAL_ACTIONS = true\n")
        config.write("TRIPLICATE = true\nHAND_LOG_FILEPATH = ./hand_logs\n")

        l = dirs + ["RANDOM"]

        if os.path.isfile('retired.txt'):
            f = open('retired.txt', 'r')
            retired = []
            for line in f:
                retired.append(line.strip())
            f.close()
            l = [x for x in l if x not in retired]

        random.shuffle(l)

        # Find the one that has played the least and force it into the first position
        uses = [(wins[x] + seconds[x] + lasts[x], x) for x in l]
        (uses, bot) = min(uses)
        l.insert(1, l.pop(l.index(bot)))

        for i in range(1, 4):
            current = l[i]
            if current == "RANDOM":
                config.write("PLAYER_%d_TYPE = RANDOM\nPLAYER_%d_NAME = RANDOM\n" % (i, i))
            else:
                config.write("PLAYER_%d_TYPE = FOLDER\nPLAYER_%d_NAME = %s\n" % (i, i, l[i]))
                config.write("PLAYER_%d_PATH = ./players/%s\n" % (i, l[i]))
        config.close()


        # What we want is to run the script
        results = subprocess.Popen(["java", "-jar", "engine_1.6.jar"], stdout=subprocess.PIPE)
        out, err = results.communicate()

        out_lines = [x.strip() for x in out.split('\n')]
        for line in out_lines:
            if 'Writing to hand log' in line:
                file_name = line.split("Writing to hand log: ")[1]
                g = open(file_name)
                for line in g:
                    if '### ILLEGAL ACTION' in line and 'trunk' in line:
			print out, err, 'BAD TRUNK ACTION'
			srcfile = './trunk.dump'
			file_name = file_name.split('./hand_logs/')[1]
			shutil.copy(srcfile, './replayer/failures/' + file_name)

                        h = open('ILLEGAL_TRUNK_ACTIONS', 'a')
                        h.write(file_name + '\n')
                        h.close()
			break
                g.close()

        # out is the stdout of running the engine
        locations = []
        lines = out.split('\n')
        output_lines = [l for l in lines if 'Writing to hand log: ' in l]
        for output_line in output_lines:
            location = output_line.split('Writing to hand log: ')[-1]
            locations.append(location)


        game_results = []
        for location in locations:
            f = open(location, 'r')

            last_result = []
            for line in f:
                if 'Hand #' in line:
                    [hand, p1, p2, p3] = line.split(',')
                    p1name, p1val = p1.replace(')', '').split('(')
                    p2name, p2val = p2.replace(')', '').split('(')
                    p3name, p3val = p3.replace(')', '').split('(')
                    p1name = p1name.strip()
                    p2name = p2name.strip()
                    p3name = p3name.strip()
                    if p1name not in scores: p1name = p1name[:-1]
                    if p2name not in scores: p2name = p2name[:-1]
                    if p3name not in scores: p3name = p3name[:-1]
                    last_result = [(p1name.strip(), int(p1val)),
                                   (p2name.strip(), int(p2val)),
                                   (p3name.strip(), int(p3val))]
            f.close()
            game_result = sorted(last_result, key=lambda x: x[1], reverse=True)
            game_results.append(game_result)

        for [(winner, _), (second, _), (loser, _)] in game_results:
            scores[winner] += 100
            scores[second] -= 20
            scores[loser] -= 80
            wins[winner] += 1
            seconds[second] += 1
            lasts[loser] += 1

        #print 'Finished %d sets of triplicate' % (iteration + 1)

        f = open('../results.html', 'w')
        html = """
<html>
<head>
<style>
table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
}
th, td {
    padding: 5px;
}
</style>
</head>
<body>
  <table style="width:100%">
    <tr>
      <th>Name</th>
      <th>Wins</th>
      <th>Seconds</th>
      <th>Losses</th>
      <th>Total</th>
      <th>Score</th>
      <th>Mean</th>
    </tr>
"""
        f.write(html)
        for score in sorted(scores.keys()):
            #print '%s:\t%d' % (score, scores[score])
            count = sum([wins[score], seconds[score], lasts[score]])
            mean = float(scores[score]) / count if count != 0 else 0
            f.write(
        "<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td>" \
            % (score, wins[score], seconds[score], lasts[score], count))
            f.write(
        "<td>%d</td><td>%f</td></tr>\n" \
            % (scores[score], mean))

        f.write("</table><p>Simulations started at: %s</p><p>Last updated at : %s</p></body></html>" % (str(start_time), str(datetime.now())))
        f.close()


    # Cleanup the scons and sql
    results = subprocess.Popen(["rm", "scons.dump"])
    results = subprocess.Popen(["rm", "sqlite.db"])
    if p1name != 'RANDOM': results = subprocess.Popen(["rm", p1name + ".dump"])
    if p2name != 'RANDOM': results = subprocess.Popen(["rm", p2name + ".dump"])
    if p3name != 'RANDOM': results = subprocess.Popen(["rm", p3name + ".dump"])

    # Write the hand logs in case they were wanted
    f = open('replayer/runner_result', 'w')
    f.write(out)
    f.close()
