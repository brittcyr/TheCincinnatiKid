import argparse
import socket
import sys
from Global import State
from Preflop import Preflop
from Flop import Flop
from Turn import Turn
from River import River

"""
Simple example pokerbot, written in python.

This is an example of a bare bones pokerbot. It only sets up the socket
necessary to connect with the engine and then always returns the same action.
It is meant as an example of how a pokerbot should communicate with the engine.
"""
class Player:
    def run(self, input_socket):
        # Get a file-object for reading packets from the socket.
        # Using this ensures that you get exactly one packet per read.
        f_in = input_socket.makefile()
        while True:
            # Block until the engine sends us a packet.
            data = f_in.readline().strip()
            # If data is None, connection has closed.
            if not data:
                print "Gameover, engine disconnected."
                break

            # Here is where you should implement code to parse the packets from
            # the engine and act on it. We are just printing it instead.
            print data

            # When appropriate, reply to the engine with a legal action.
            # The engine will ignore all spurious responses.
            # The engine will also check/fold for you if you return an
            # illegal action.
            # When sending responses, terminate each response with a newline
            # character (\n) or your bot will hang!
            word = data.split()[0]
            if word == "GETACTION":
                action = Player.get_action(data)
                s.send("%s\n" % (action))
            elif word == "REQUESTKEYVALUES":
                # At the end, the engine will allow your bot save key/value pairs.
                # Send FINISH to indicate you're done.
                s.send("FINISH\n")
            elif word == "NEWGAME":
                State.new_game(data)
            elif word == "NEWHAND":
                State.new_hand(data)
            elif word == "HANDOVER":
                State.handover(data)


            # GETACTION potSize numBoardCards [boardCards] [stackSizes] numActivePlayers [activePlayers] numLastActions [lastActions] numLegalActions [legalActions] timebank

            # HANDOVER [stackSizes] numBoardCards [boardCards] numLastActions [lastActions] timeBank


        # Clean up the socket.
        s.close()


    @classmethod
    def get_action(cls, data):
        # Decide which class to use
        # GETACTION potSize numBoardCards [boardCards] [stackSizes] numActivePlayers [activePlayers] numLastActions [lastActions] numLegalActions [legalActions] timebank

        numBoardCards = int(data.split()[2])

        # TODO: Use different players
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
    parser = argparse.ArgumentParser(description='A Pokerbot.', add_help=False, prog='pokerbot')
    parser.add_argument('-h', dest='host', type=str, default='localhost', help='Host to connect to, defaults to localhost')
    parser.add_argument('port', metavar='PORT', type=int, help='Port on host to connect to')
    args = parser.parse_args()

    # Create a socket connection to the engine.
    print 'Connecting to %s:%d' % (args.host, args.port)
    try:
        s = socket.create_connection((args.host, args.port))
    except socket.error as e:
        print 'Error connecting! Aborting'
        exit()

    bot = Player()
    bot.run(s)
