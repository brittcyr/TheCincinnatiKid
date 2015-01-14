import subprocess


if __name__ == '__main__':
    # TODO: Take an argument for the number of times to run
    # TODO: Make the number of players variable

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

    scores = {}
    scores[p1name.strip()] = 0
    scores[p2name.strip()] = 0
    scores[p3name.strip()] = 0

    for [(winner, _), (second, _), (loser, _)] in game_results:
        scores[winner] += 100
        scores[second] -= 20
        scores[loser] -= 80

    for score in sorted(scores.keys()):
        print '%s:\t%d' % (score, scores[score])


    # Cleanup the scons and sql
    results = subprocess.Popen(["rm", "scons.dump"])
    results = subprocess.Popen(["rm", "sqlite.db"])

    # Write the hand logs in case they were wanted
    f = open('replayer/runner_result', 'w')
    f.write(out)
    f.close()
