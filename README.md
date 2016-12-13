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

If you are running the program on bash, a raw_input() may show up before everything finishes printing. So if the cursor is stuck for more than 15 seconds and "Calculating...", "Player is thinking..." or "Getting player's rule..." is not what was printed previously, please type "Y" or "N" and hit enter. This happened in one of our teams member's machine when using Git Bash to run python programs. We were not able to test it in many different setups but it works fine on Windows Command Prompt and PowerShell.

-----------------------------------------------
## Changes made to game.py

We have made a few changes to the game.py file provided by the TAs and combined them to our scientist.py module. We made it so that the adversaries wait until at least 20 cards have been played in order to decide game end. We also made it so that the adversary would pick a new card after playing one.

-----------------------------------------------
## Changes made to new_eleusis.py

1. Added code in is_value(card) to convert the Card to String format.
2. Added code in is_card(card) to convert the Card to String format.
3. Updated code in less(a,b) in elif is_value(a) part to convert a into number_to_value(int(a))
4. Updated plus1 and minus1 code to cycle through in case of String
5. Updated plus1 and minus1 code to remove assertion for value<13 and value>1 because once it reaches King and Ace respectively, it gives an assertion error
6. Updated diff_suit and diff_value to return -1,+1,Positive and Negative so that can be used in creating minus1,plus1,Greater and less rules.

-----------------------------------------------
## Phase 2 Rule Creation Details :

<<<<<<< HEAD
For Phase-2 of Eleusis, we are using Decomposition Algorithm to create rules by reading all the correct cards in the BoardState. Basically, Decomposition Algorithm creates rules in the IF-THEN format. This works by using a Dictionary where all the keys are list of all the attributes of the previous card and the values are all the attributes of the next CORRECT card. Then each of the attributes of the next card are generalized to avoid overfitting of the data. After generalization, we convert these mappings from their dictionary format to string format. Using the OR and AND on all such mappings, we create a list of rules and sort them on the basis of their efficiency, logical equivalence and rule-length. Efficiency is measured on all the CORRECT Cards. Logical Equivalence is measured on all the CORRECT and INCORRECT Cards. When the player is required to display his rule, he chooses the rule that is highest on efficiency, equivalence and lowest on rule length.
=======
For Phase-2 of Eleusis, we are using Decomposition Algorithm to create rules by reading all the correct cards in the BoardState. Basically, Decomposition Algorithm creates rules in the IF-THEN format. This works by using a Dictionary where all the keys are list of all the attributes of the previous card and the values are all the attributes of the next CORRECT card. Then each of the attributes of the next card are generalized to avoid overfitting of the data. After generalization, we convert these mappings from their dictionary format to string format. Using the OR and AND on all such mappings, we create a list of rules and sort them on the basis of their efficiency, logical equivalence and rule-length. Efficiency is measured on all the CORRECT Cards. Logical Equivalence is measured on all the CORRECT and INCORRECT Cards. When the player is required to display his rule, he chooses the rule that is highest on efficiency, equivalence and lowest on rule length.
>>>>>>> d353fef828c1028ee4dd488f9f92e32d00888744
