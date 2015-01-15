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


Version Log
===========

| Version   | Date  | Summary of Changes                    |
|-----------|:-----:|---------------------------------------|
| v0        |1/14   | First working player to beat random   |
| v1        |1/15   | Improved flop play                    |
