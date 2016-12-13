# Eleusis

Project Phase 2

CMSC 671

-----------------------------------------------
## Contributors

- Harsh Vashishta
- Sabin Raj Tiwari
- Shantanu Sengupta
- Sushant Chaudhari

-----------------------------------------------
## Running the program:

python scientist.py \<initial cards\> '\<rule\>'

### E.g.

python scientist.py 3D "if(equal(color(previous),R),equal(color(current),B),if(equal(color(previous),B),equal(color(current),R),))"

-----------------------------------------------
## Changes made to game.py

We have made a few changes to the game.py file provided by the TAs and combined them to our scientist.py module. We made it so that the adversaries wait until at least 20 cards have been played in order to decide game end. We also made it so that the adversary would pick a new card after playing one.

-----------------------------------------------
## Changes made to new_eleusis.py

1. Added code in is_value(card) to convert the Card to String format.
2. Added code in is_card(card) to convert the Card to String format.
3. Updated code in less(a,b) in elif is_value(a) part to convert a into number_to_value(int(a))
4. Updated plus1 and minus1 code to cycle through in case of String
5. Updated plus1 and minus1 code to remove assertion for value<13 because once it reaches King and Ace respectively, it gives an assertion    error
6. Updated diff_suit and diff_value to return -1,+1,Positive and Negative so that can be used in creating plus1,minus1,Greater and less rules.
