# Eleusis

Project Phase 2

CMSC 671

-----------------------------------------------
## Contributors

- Sushant Chaudhari
- Shantanu Sengupta
- Sabin Raj Tiwari
- Harsh Vashishta

-----------------------------------------------
## Running the program:

python scientist.py \<initial cards\> '\<rule\>'

### E.g.

python scientist.py 3D "if(equal(color(previous),R),equal(color(current),B),if(equal(color(previous),B),equal(color(current),R),))"

-----------------------------------------------
## Changes made to game.py

We have made a few changes to the game.py file provided by the TAs and combined them to our scientist.py module. We made it so that the adversaries wait until at least 20 cards have been played in order to decide game end. We also made it so that the adversary would pick a new card after playing one.
