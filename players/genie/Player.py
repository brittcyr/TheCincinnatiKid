import argparse
import socket
import sys
import traceback
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
                try:
                    action = Player.get_action(data)
                    if ':' in action:
                        try:
                            amount = int(action.split(':')[-1])
                            # Do not push a lot of chips if it is not a good spot
                            if amount >= 40:
                                if State.current_result == False:
                                    # This might be illegal, so it will force fold
                                    action = "CHECK"
                                    print 'CHECK/FOLD LOSING HAND'
                        except Exception as e:
                            print e
                    if 'FOLD' in action:
                        if State.current_result == True:
                            # CALL instead
                            call = [x for x in data.split() if 'CALL' in x][-1]
                            action = call
                            print 'CALL WINNING HAND'

                    s.send("%s\n" % (action))
                except Exception as e:
                    print 'ERROR IN THE CODE'
                    print e
                    print traceback.format_exc()
                    s.send("CHECK\n")

            elif word == "REQUESTKEYVALUES":
                # At the end, the engine will allow your bot save key/value pairs.
                # Send FINISH to indicate you're done.
                s.send("FINISH\n")
            elif word == "NEWGAME":
                try:
                    State.new_game(data)
                except:
                    pass
            elif word == "NEWHAND":
                try:
                    State.new_hand(data)
                except:
                    pass
            elif word == "HANDOVER":
                try:
                    State.handover(data)
                except:
                    pass

        # Clean up the socket.
        s.close()


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
