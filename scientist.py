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
            end = True

        adv2 = adversary2.play()
        if new_eleusis.is_card(adv2):
            player.play(adv2)   
        else:
            end = True

        adv3 = adversary3.play()
        if new_eleusis.is_card(adv3):
            player.play(adv3)   
        else:
            end = True

        print "Round Ended"
        print player.board_state()

    print "Game Ended"

    
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
        for card in cards:
            self.play(card)
        self.setup_thinker(cards, dealer_rule)

    #region Setup methods

    # This functions sets up the scientist logic module
    def setup_thinker(self, cards, dealer_rule):
        card_objs = []
        for card in cards:
            card_objs.append(think.Card(card[0], card[1]))
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
            return rules[0][0]
        return None
    
    #	This function will create the board state in string representation
    #	Returns string for the board
    def board_state(self):
        board = "{\n"
        for card in self.board:
            board = board + "(" + card[0] + ", " + str(card[1]) + ")\n"
        board = board.strip(" ").strip(",")
        board = board + "}"
        return board

    #	This function will play a card and determine if it satisfies the rule.
    #	This also updates the board_state.
    #	Returns true or false
    def play(self, card):
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
            return self.thinker.guessed_rule
        else:
            card = self.get_best_card()
            self.thinker.playNext(think.Card(card[0], card[1]))
            correct = self.play(card)    
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
        for card in self.board:
            score = score + 1 + (2 * len(card[1]))
        if not(self.player_rule_str == self.dealer_rule_str):
            score = score + 15
        cards = []
        for card in self.board:
            cards.append(card[0])
        original_board = list(self.board)
        self.board = []
        # play with the player rule applied
        for card in original_board:
            self.play(card[0], self.player_rule)
        print "\nThe Board State (using the player rule and only playing the correct cards for the dealer rule): "
        print self.board_state() + "\n"
        # add to the score if there is a difference
        correct_dealer = len(original_board)
        correct_player = len(self.board)
        efficiency = (correct_player / float(correct_dealer)) * 100.0
        if not(correct_dealer == correct_player):
            score = score + 30
        print "\nEfficiency: " + str(efficiency)
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
        try:
            correct_cards = []
            incorrect_cards = []
            player_rule = new_eleusis.parse(self.thinker.guessed_rule)
            # for all the cards in the hand, assign correct or 
            #   incorrect against the player's current rule
            for card in self.hand:
                if evaluate_card(card, player_rule):
                    correct_cards.append(card)
                else:
                    incorrect_cards.append(card)
            # if the last play made was a positive test, play a negative
            if self.last_play_positive:
                self.last_play_positive = False
                # if there are incorrect cards in the hand
                if len(incorrect_cards) > 0:
                    return incorrect_cards[int(round(random.random() * (len(self.incorrect_cards) - 1)))]
                else:
                    return correct_cards[int(round(random.random() * (len(self.correct_cards) - 1)))]
            else:
                self.last_play_positive = True
                 # if there are correct cards in the hand
                if len(correct_cards) > 0:
                    return correct_cards[int(round(random.random() * (len(self.correct_cards) - 1)))]
                else:
                    return incorrect_cards[int(round(random.random() * (len(self.incorrect_cards) - 1)))]
        except:
            return self.get_random_card()
    
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
                evaluation.append((rule, self.evaluate_rule(new_eleusis.parse(rule))))
            except:
                evaluation.append((rule, 0.0))
        return sort(evaluation)

    #	Evaluates a rule based on how many correct and wrong cards it produced.
    #	Returns the value for the evaluation (0 - 100)
    def evaluate_rule(self, rule):
        total = 0
        correct = 0
        for card in self.board:
            total = total + 1
            if rule.evaluate(card[0]):
                correct = correct + 1
        return (correct / total) * 100

    #	Calculates if the player should decide success
    #	Returns true or false depending on the player needing to decide
    def decide_success(self):
        current_rule = self.rule()
        if not current_rule is None:
            if len(self.board) > 20 and current_rule.evaluate(board):
                if rule.evaluation == 100 or self.total_moves > 200:
                    return True
        return False

    #	Builds the list of all possible cards
    def build_all_cards(self):
        for value in card_values:
            for suit in card_suits:
                self.all_cards.append(value + suit)

    #	Gets a random card to play from the hand
    #	Returns a card.
    def get_random_card(self):
        return self.hand.pop(int(round(random.random() * (len(self.hand) - 1))))

    #end Helper Functions

#end Scientist class

main(sys.argv)