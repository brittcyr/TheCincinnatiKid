TheCincinnatiKid
================
----------------
Overview
--------
This is the Britt Cyr submission to MIT Pokerbots 2015.

Helper Scripts
--------------
###replayer.py
First put the individual hand log into hand, then run
python replayer.py -h HERO.
This puts the actions into action.
Then go the the player and run python SingleHandPlayer.py.
You can use print statements to output what the bot is thinking to help debug.

###runner.py
This script is used for running tournaments. 
It will automatically pull the bots and run them. 
Then there will be a result.html up a directory which will have the 
table of the results that gets updated every time a tournament finishes.

###hand_log_converter.py
This converts hand histories into pokerstars format.
It does not properly handle sidepots but those are rare enough to
not worry about. This is used to send the hands to pokertracker for
statistical analysis.

###DeckDecoder.java
This replicates the shuffle used in the casino and possibly in tournaments.
From decompiling the engine, there was a significant vulnerability. The
shuffle is deterministic and predictable. Once you can reverse the name
anonymizer through a brute force guessing of all possible teams, you can
retrieve the shuffle for the day. This actually worked for looking back at
casinos and accurately predicting the cards opponents would have.
Another vulnerability not exploited in this bot is that there are AWS keys
to the server running the tournament hard coded into the engine. This
is bad since someone could just log in and update the database of results
to change the tournament result.

Version Log
===========

| Version   | Date  | Summary of Changes                    |
|-----------|:-----:|---------------------------------------|
| v0        |1/14   | First working player to beat random   |
| v1        |1/15   | Improved flop play                    |
| v2        |1/16   | Improved turn play                    |
| v3        |1/17   | Improved river play                   |
| v4        |1/19   | Devalued pair and two pair            |
| v5        |1/20   | Changing constants and devalue pair   |
| v6        |1/22   | Reset preflop hand rankings           |
| genie     |1/24   | Predict the future                    |
