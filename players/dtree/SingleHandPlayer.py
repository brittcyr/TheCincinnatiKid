import argparse
import socket
import sys
from Global import State
from Preflop import Preflop
from Flop import Flop
from Turn import Turn
from River import River

"""
A copy of the regular player, but it is just for replaying a specific hand
"""
class Player:
    def run(self, file_to_read):
        f = open(file_to_read, 'r')
        for line in f:
            # Block until the engine sends us a packet.
            data = line.strip()
            # If data is None, connection has closed.
            if not data:
                print "Gameover, engine disconnected."
                break

            # Here is where you should implement code to parse the packets from
            # the engine and act on it. We are just printing it instead.

            # When appropriate, reply to the engine with a legal action.
            # The engine will ignore all spurious responses.
            # The engine will also check/fold for you if you return an
            # illegal action.
            # When sending responses, terminate each response with a newline
            # character (\n) or your bot will hang!
            word = data.split()[0]
            if word == "GETACTION":
                action = Player.get_action(data)
            elif word == "REQUESTKEYVALUES":
                # At the end, the engine will allow your bot save key/value pairs.
                # Send FINISH to indicate you're done.
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
            action = Flop.get_action(data)
        elif numBoardCards == 5:
            # RIVER
            action = Flop.get_action(data)

        if not action:
            action = "CHECK"

        return action




if __name__ == '__main__':
    bot = Player()
    bot.run('/afs/athena.mit.edu/user/c/y/cyrbritt/workspace/poker/actions')
