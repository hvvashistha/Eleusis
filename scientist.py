# -*- coding: utf-8 -*-

# Project Phase 1
# CMSC 671

#   Sabin Raj Tiwari
#   Shantanu Sengupta
#   Harsh Vashishta
#   Sushant Chaudhari

# References for the code
#   https://docs.python.org/
#   https://docs.python.org/2.7/tutorial/datastructures.html
#   https://docs.python.org/2/library/itertools.html#itertools.product
#   https://www.tutorialspoint.com/python/python_command_line_arguments.htm
#   http://stackoverflow.com/questions/1228299/change-one-character-in-a-string-in-python
#   http://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float-in-python

import sys
import random
import new_eleusis
import datetime
import think
import game

# globals
card_values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
card_suits = ['C', 'D', 'H', 'S']
card_colors = {
    'C' : 'B',
    'D' : 'R',
    'H' : 'R',
    'S' : 'B'
}

#main method
def main(args):
    del args[0]
    print "Calculating..."
    time_start = datetime.datetime.now()

    cards = []
    for i in range(0, len(args) - 1):
        cards.append(args[i])

    player = Scientist(cards, args[-1])
    adversary1 = game.Adversary()
    adversary2 = game.Adversary()
    adversary3 = game.Adversary()

    end = False
    while not end:
        player_play = player.scientist()
        if not new_eleusis.is_card(player_play):
            end = True

        adv1 = adversary1.play()
        if new_eleusis.is_card(adv1):
            player.play(adv1)   
        else:
            print "\nAdversary 1 wants to show the rule: "
            print adv1
            end = True

        adv2 = adversary2.play()
        if new_eleusis.is_card(adv2):
            player.play(adv2)   
        else:
            print "\nAdversary 2 wants to show the rule: "
            print adv2
            end = True

        adv3 = adversary3.play()
        if new_eleusis.is_card(adv3):
            player.play(adv3)   
        else:
            print "\nAdversary 3 wants to show the rule: "
            print adv3
            end = True

        print player.board_state()
        print "\n"
    
    print "\nPlayer's Rules Is:"
    print player.rule()

    
    # print "\nThe rule that was guessed after 200 moves is (as a dictionary): "
    # print game.guessed_rule_dict

    # print "\nThe rule that was guessed after 200 moves is (as an expression): "
    # print game.guessed_rule

    # scientist = scientist.Scientist(game.history, game.provided_rule, game.guessed_rule)
    # print "\nThe total score for the player is: " + str(scientist.score())

    # print "\nThe rule that was guessed after 200 moves is (as a dictionary): "
    # print game.guessed_rule_dict

    # print "\nThe rule that was guessed after 200 moves is (as an expression): "
    # print game.guessed_rule

    # time_end =  datetime.datetime.now()
    # print "\nTime Taken (h:m:s.ms): " + str(time_end - time_start)


# This class has a few player functions that are not used in phase 1
# But this is also used to score the player and end the game for phase 1

class Scientist:

    def __init__(self, cards, dealer_rule):
        self.correct_moves = 0
        self.incorrect_moves = 0
        self.board = []
        self.all_cards = []
        self.build_all_cards()
        self.hand = []
        self.thinker = None
        self.get_cards(14)
        self.last_play_positive = True
        self.setup_thinker(cards, dealer_rule)
        for card in cards:
            self.play(card)
        

    #region Setup methods

    # This functions sets up the scientist logic module
    def setup_thinker(self, cards, dealer_rule):
        card_objs = []
        for card in cards:
            card_objs.append(think.Card(card[:-1], card[-1]))
        self.thinker = think.Game(card_objs, dealer_rule, randomPlay = False)

    # This function gets a count of random cards and adds it to the hand
    def get_cards(self, count):
        for i in range(0, count):
            self.hand.append(self.all_cards[int(round(random.random() * (len(self.all_cards) - 1)))])        

    #end Setup methods

    #region Main Functions

    #	This function will set the dealer rule using the
    #	helper functions in new_eleusis.py.
    #	TODO: Need to update a few things based on prof's suggestions.
    def set_rule(self, dealer_rule, player_rule):
        self.dealer_rule = new_eleusis.parse(dealer_rule)

    # 	This function will return the current actual rule that the player is
    #	considering and will be used to determine the score.
    #	Returs the best rule in the list of rules
    def rule(self):
        if len(self.thinker.guessed_rules) > 0:
            rules = self.prioritize_rules(self.thinker.guessed_rules)
            return rules[-1]
        return None
    
    #	This function will create the board state in string representation
    #	Returns string for the board
    def board_state(self):
        board = "\nRound Ended: {\n"
        for card in self.board:
            board = board + "\t {" + card[0] + "} , Incorrect Cards " + str(card[1]) + "\n"
        board = board.strip(" ").strip(",")
        board = board + "}"
        return board

    #	This function will play a card and determine if it satisfies the rule.
    #	This also updates the board_state.
    #	Returns true or false
    def play(self, card):
        self.thinker.playNext(think.Card(card[:-1], card[-1]))
        if len(self.board) > 0:
            if self.evaluate_card(card, self.thinker.dealer_rule):
                self.board.append((card, []))
                return True
            else:
                self.board[len(self.board) - 1][1].append(card)
                return False
        else:
            self.board.append((card, []))
            return True

    #	This function handles the player which will determine when and what to play
    #	and choosing when to declare success.
    def scientist(self):
        if self.decide_success() or len(self.thinker.history) >= 200:
            return self.rule()[0]
        else:
            card = self.get_best_card()
            correct = self.play(card)
            self.get_cards(1)
            if correct:                
                self.correct_moves = self.correct_moves + 1
            else:
                self.incorrect_moves = self.incorrect_moves + 1
            return card
       

    #	Adds 1 for every right card, 2 for every wrong card, 15 for a wrong rule, 
    #		and 30 for a rule that does not satisfy the cards on the board.
    #	Returns a value for the score
    def score(self):
        score = 0
        
        return score

    #end Main Functions



    #region Helper Functions


    # Evaluates a card with the provided rule.
    # Returns True or False.
    def evaluate_card(self, card, rule):
        last_three = []
        if len(self.board) > 0:
            last_three.append(self.board[-1][0])
        else:
            last_three.insert(1, None)
        if len(self.board) < 2:
            last_three.insert(0, None)
        else:
            last_three.insert(0, self.board[-2][0])
        last_three.append(card)

        if rule.evaluate(last_three):
            return True
        else:
            return False

    #	Based on the current possible rules, decides the best card to play.
    #	Applies constrainsts at this stage.
    #	Returns the card to play.
    def get_best_card(self):
        index = -1
        try:
            correct_indeces = []
            incorrect_indeces = []
            player_rule = new_eleusis.parse(self.rule())
            # for all the cards in the hand, assign correct or 
            #   incorrect against the player's current rule
            for i in range(0, len(self.hand)):
                if evaluate_card(self.hand[i], player_rule):
                    correct_indeces.append(i)
                else:
                    incorrect_indeces.append(i)
            # if the last play made was a positive test, play a negative
            if self.last_play_positive:
                self.last_play_positive = False
                # if there are incorrect cards in the hand
                if len(incorrect_indeces) > 0:
                    index = incorrect_indeces[int(round(random.random() * (len(self.incorrect_indeces) - 1)))]
                else:
                    index = correct_indeces[int(round(random.random() * (len(self.correct_indeces) - 1)))]
            else:
                self.last_play_positive = True
                 # if there are correct cards in the hand
                if len(correct_indeces) > 0:
                    index = correct_indeces[int(round(random.random() * (len(self.correct_indeces) - 1)))]
                else:
                    index = incorrect_indeces[int(round(random.random() * (len(self.incorrect_indeces) - 1)))]
        except:
            # if the rule evaluation fails
            index = -1
        
        #play the card with the corresponding index
        return self.get_card_from_hand(index)
    

    #	Generates rules that apply to the current state of the board. 
    #	Only a decent amount will be chosen sicne there could be infinute possible rules.
    #	Applies constraints at this stage.
    # 	TODO: Infer Rules
    def generate_rules(self):
        correct_rules = []
        return correct_rules


    #	Sets priority to all the rules that are being considered currently.
    #	Uses a list of rules that contain the attribute: evaluation
    #	Returns the sorted list of rules.
    def prioritize_rules(self, rules):
        evaluation = []
        for rule in rules:
            try:
                parsed_rule = new_eleusis.parse(rule)
                value = self.evaluate_rule(parsed_rule)
                evaluation.append((rule, value))
            except:
                evaluation.append((rule, (0.0, 100.0)))
        return sorted(evaluation, key = lambda tuple: (tuple[1][0], tuple[1][1]))


    # Gets the efficiency of a provided rule
    def get_efficiency(self, rule):
        total = 0
        correct = 0
        for card in self.board:
            total = total + 1
            if self.evaluate_card(card[0], rule):
                correct = correct + 1
        return (correct / float(total)) * 100
    
    
    # Gets the logical equivalence of a provided rule
    def get_equivalence(self, rule):
        match = 0
        total = len(self.thinker.history)
        for card in self.thinker.history:
            player = self.evaluate_card(str(card[0]), rule)
            dealer = self.evaluate_card(str(card[0]), self.thinker.dealer_rule)
            if dealer == player:
                match = match + 1
        return (match / float(total)) * 100


    #	Evaluates a rule based on how many correct and wrong cards it produced.
    #	Returns the value for the efficiency and equivalence (0 - 100)
    def evaluate_rule(self, rule):
        efficiency = self.get_efficiency(rule)        
        equivalence = self.get_equivalence(rule)
        return (efficiency, equivalence)

    #	Calculates if the player should decide success
    #	Returns true or false depending on the player needing to decide
    def decide_success(self):
        current_rule = self.rule()
        history_length = len(self.thinker.history)
        if not current_rule is None:
            try:
                parsed_rule = new_eleusis.parse(current_rule[0])
                #if there have been more than 20 plays
                if history_length > 20:
                    # if the current rule has 100 efficiency and 100 equivalence
                    if current_rule[1][0] == 100 and current_rule[1][1] == 100:
                        return True
                    # if the current rule has 100 efficiency or 100 equivalence
                    elif current_rule[1][0] == 100 or current_rule[1][1] == 100:
                        return True
                    # if the current rule is not as efficient as we like, show rule if 200 plays have been made
                    elif history_length >= 200:
                        return True
            except:
                if history_length >= 200:
                    return True
        return False


    #	Builds the list of all possible cards
    def build_all_cards(self):
        for value in card_values:
            for suit in card_suits:
                self.all_cards.append(value + suit)


    #	Gets a to play from the hand
    #	Returns a card.
    def get_card_from_hand(self, index):
        if index < 0:
            return self.hand.pop(int(round(random.random() * (len(self.hand) - 1))))
        else:
            return self.hand.pop(index)

    #end Helper Functions

#end Scientist class

main(sys.argv)