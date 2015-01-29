import argparse
import socket
import traceback
import sys
from Global import State
from Preflop import Preflop
from Flop import Flop
from Turn import Turn
from River import River
from random import random

"""
A copy of the regular player, but it is just for replaying a specific hand
"""
class Player:
    def run(self, file_to_read):
        f = open(file_to_read, 'r')
        for line in f:
            data = line.strip()
            # If data is None, connection has closed.
            if not data:
                print "Gameover, engine disconnected."
                break

            word = data.split()[0]
            if word == "GETACTION":
                action = Player.get_action(data)
                try:
                    action = Player.get_action(data)
                    if ':' in action:
                        try:
                            amount = int(action.split(':')[-1])
                            # Do not push a lot of chips if it is not a good spot
                            if amount >= 30:
                                if State.current_result == False and random() < .9:
                                    # This might be illegal, so it will force fold
                                    action = "CHECK"
                                    print 'CHECK/FOLD LOSING HAND'
                        except Exception as e:
                            print e
                    if 'FOLD' in action:
                        if State.current_result == True and random() < .7:
                            # CALL instead
                            call = [x for x in data.split() if 'CALL' in x][-1]
                            action = call
                            print 'CALL WINNING HAND'

                    #s.send("%s\n" % (action))
                    print action
                except Exception as e:
                    print 'ERROR IN THE CODE'
                    print e
                    print traceback.format_exc()
                    #s.send("CHECK\n")

            elif word == "REQUESTKEYVALUES":
                pass
            elif word == "NEWGAME":
                State.new_game(data)
            elif word == "NEWHAND":
                State.new_hand(data)
            elif word == "HANDOVER":
                State.handover(data)

        f.close()

    @classmethod
    def get_action(cls, data):
        # Decide which class to use
        numBoardCards = int(data.split()[2])

        if numBoardCards == 0:
            # PREFLOP
            action = Preflop.get_action(data)
        elif numBoardCards == 3:
            # FLOP
            action = Flop.get_action(data)
        elif numBoardCards == 4:
            # TURN
            action = Turn.get_action(data)
        elif numBoardCards == 5:
            # RIVER
            action = River.get_action(data)

        if not action:
            action = "CHECK"

        print action
        return action


if __name__ == '__main__':
    bot = Player()
    bot.run('/afs/athena.mit.edu/user/c/y/cyrbritt/Downloads/MiniTournament_Mini-Tournament-Round-2_TheCincinnatiKid_vs_CJK_vs_kerbopots_p2.dump')
