import subprocess
import argparse
import os
import random
import math


if __name__ == '__main__':
    # TODO: Make the number of players variable
    parser = argparse.ArgumentParser(description='Run tournament.', add_help=False, prog='pokerbot')
    parser.add_argument('-t', dest='times', type=int, default=1, help='Times to run')
    args = parser.parse_args()

    dirs = [x for x in os.listdir("players") if os.path.isdir("players/" + x)]

    scores = {}
    wins = {}
    seconds = {}
    lasts = {}

    for iteration in xrange(args.times):
        new_dirs = [x for x in os.listdir("players") if os.path.isdir("players/" + x)]
        if new_dirs != dirs:
            dirs = new_dirs
            scores = {}
            wins = {}
            seconds = {}
            lasts = {}

        config = file("config.txt", "w")
        config.write("BIG_BLIND = 2\nSTARTING_STACK = 200\nNUMBER_OF_HANDS = 1000\n")
        config.write("CONNECTION_TIMEOUT = 2\nTIME_RESTRICTION_PER_GAME = 10\n")
        config.write("ENFORCE_TIMING_RESTRICTION = true\nDISPLAY_ILLEGAL_ACTIONS = true\n")
        config.write("TRIPLICATE = true\nHAND_LOG_FILEPATH = ./hand_logs\n")

        l = dirs + ["random"]
        random.shuffle(l)
        for i in range(1, 4):
            current = l[i]
            if current == "random":
                config.write("PLAYER_%d_TYPE = RANDOM\nPLAYER_%d_NAME = RANDOM\n" % (i, i))
            else:
                config.write("PLAYER_%d_TYPE = FOLDER\nPLAYER_%d_NAME = %s\n" % (i, i, l[i]))
                config.write("PLAYER_%d_PATH = ./players/%s\n" % (i, l[i]))
        config.close()


        # What we want is to run the script
        results = subprocess.Popen(["java", "-jar", "engine_1.4.jar"], stdout=subprocess.PIPE)
        out, err = results.communicate()

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
                    last_result = [(p1name.strip(), int(p1val)),
                                   (p2name.strip(), int(p2val)),
                                   (p3name.strip(), int(p3val))]
            f.close()
            game_result = sorted(last_result, key=lambda x: x[1], reverse=True)
            game_results.append(game_result)

        if p1name.strip() not in scores:
            scores[p1name.strip()] = 0
            wins[p1name.strip()] = 0
            seconds[p1name.strip()] = 0
            lasts[p1name.strip()] = 0

        if p2name.strip() not in scores:
            scores[p2name.strip()] = 0
            wins[p2name.strip()] = 0
            seconds[p2name.strip()] = 0
            lasts[p2name.strip()] = 0

        if p3name.strip() not in scores:
            scores[p3name.strip()] = 0
            wins[p3name.strip()] = 0
            seconds[p3name.strip()] = 0
            lasts[p3name.strip()] = 0

        for [(winner, _), (second, _), (loser, _)] in game_results:
            scores[winner] += 100
            scores[second] -= 20
            scores[loser] -= 80
            wins[winner] += 1
            seconds[second] += 1
            lasts[loser] += 1

        print 'Finished %d sets of triplicate' % (iteration + 1)

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
            print '%s:\t%d' % (score, scores[score])
            count = sum([wins[score], seconds[score], lasts[score]])
            mean = float(scores[score]) / count
            f.write(
        "<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td>" \
            % (score, wins[score], seconds[score], lasts[score], count))
            f.write(
        "<td>%d</td><td>%f</td></tr>\n" \
            % (scores[score], mean))

        f.write("</table></body></html>")
        f.close()


    # Cleanup the scons and sql
    results = subprocess.Popen(["rm", "scons.dump"])
    results = subprocess.Popen(["rm", "sqlite.db"])
    results = subprocess.Popen(["rm", p1name.strip() + ".dump"])
    results = subprocess.Popen(["rm", p2name.strip() + ".dump"])
    results = subprocess.Popen(["rm", p3name.strip() + ".dump"])

    # Write the hand logs in case they were wanted
    f = open('replayer/runner_result', 'w')
    f.write(out)
    f.close()
