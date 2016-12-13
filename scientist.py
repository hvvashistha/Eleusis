# -*- coding: utf-8 -*-

# Project Phase 2
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
import thinker

# globals
global min_plays
global max_plays
min_plays = 20
max_plays = 200
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
    adversaries = [Adversary(), Adversary(), Adversary()]
    rounds = 0
    end = -2

    while end == -2:
        rounds = rounds + 1
        print "\n========================================="
        print "Round " + str(rounds)
        print "========================================="
        print "Current Board: " + player.board_state()
        print "\n"
    
        # The Player makes a move
        move_time_start = datetime.datetime.now()
        print "Player is thinking..."
        player_play = player.scientist()
        move_time_end = datetime.datetime.now()
        if new_eleusis.is_card(player_play):
            print "Player Played: " + player_play + " [time taken (h:m:s.ms): " + str(move_time_end - move_time_start) + "]"
        else:
            print "Ending Board: " + player.board_state()
            print "\nPlayer wants to show the rule."
            end = -1
            break

        history_length = len(player.thinker.history)
        # All the adversaries make their moves
        for i in range(0, len(adversaries)):
            move_time_start = datetime.datetime.now()
            play = adversaries[i].play(history_length)
            move_time_end = datetime.datetime.now()
            if new_eleusis.is_card(play):
                print "Adversary " + str(i + 1) + " Played: " + play + " [time taken (h:m:s.ms): " + str(move_time_end - move_time_start) + "]"
                is_correct = player.play(play)
                adversaries[i].update_score(is_correct, history_length)
            else:
                print "\nAdversary " + str(i + 1) + " wants to show the rule."
                print "\nEnding Board: " + player.board_state()
                end = i
                break

    time_end =  datetime.datetime.now()
    
    # Print the results
    print "\n========================================="
    print "Total Game Time (h:m:s.ms): " + str(time_end - time_start)
    print "Results for the Game (rules and scores):"
    print "========================================="
    # Print the information for the adversaries' rules and scores
    for index in range(0, len(adversaries)):
        name = "Adversary " + str(index + 1)
        if index == end:
            name = name + " (called end of game)"
        print name 
        print "\tRule: " + str(adversaries[index].rule)
        adv_score = score(player, adversaries[index].rule, adversaries[index].score, index == end)
        print "\tEfficiency: " + str(adv_score[1]) + " %"
        print "\tEquivalence: " + str(adv_score[2]) + " %"
        print "\tScore: " + str(adv_score[0])
        print "-----------------------------------------"
    
    # Print the information for the player's rule and score
    name = "Player"
    if end == -1:
        name = name + " (called end of game)"
    print name
    print "Getting Player's Rule..."
    if end != -1:
        player.get_rule()
    if player.rule is None:
        print "\tRule: " + player.generate_random_rule()
        print "\n\tPlayer's Score: " + str(player.get_score(False, end == -1))
    else:
        # if the player's rule is npt empty
        print "\tRule: " + str(player.rule[0])
        print "\tEfficiency: " + str(player.rule[1][0]) + " %"
        print "\tEquivalence: " + str(player.rule[1][1]) + " %"
        confidence_param = 100
        if player.rule[1][1] < 100.0:
            confidence_param = 100 - player.rule[1][1]
        print "\tConfidence: " + str((player.rule[1][0] / 100) * (player.rule[1][1] / 100) * (confidence_param / 100) * player.confidence * 100) + " %"
        input = ""
        while not(input == "Y" or input == "y" or input == "N" or input == "n"):
            input = raw_input("\nWas the player's rule logically equivalent? (Y/N):")
        print "\n\tPlayer's Score: " + str(player.get_score(input == "Y" or input == "y", end == -1))
        print "-----------------------------------------"

# Gets the total score based on a rule and the score for the plays
def score(scientist, rule, score, is_ending_player):
    efficiency = 0.0
    equivalence = 0.0
    if rule is None:
        score = score + 30
    try:
        parsed_rule = new_eleusis.parse(rule)
        efficiency = scientist.get_efficiency(parsed_rule)
        equivalence = scientist.get_equivalence(parsed_rule)
        if efficiency != 100.0:
            score = score + 15
        if equivalence == 100.0:
            score = score - 75
            if is_ending_player:
                score = score - 25
        else:
            score = score + 30
    except:
        score = score + 45
    return (score, efficiency, equivalence)        
    

# This class has a few player functions that are not used in phase 1
# But this is also used to score the player and end the game for phase 1

class Scientist:

    def __init__(self, cards, dealer_rule):
        self.score = 0
        self.num_initial_cards = len(cards)
        self.rule = None
        self.rules = []
        self.confidence = 1
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
            card_objs.append(thinker.Card(card[:-1], card[-1]))
        self.thinker = thinker.Game(card_objs, dealer_rule, randomPlay = False)

    # This function gets a count of random cards and adds it to the hand
    def get_cards(self, count):
        for i in range(0, count):
            self.hand.append(self.all_cards[int(round(random.random() * (len(self.all_cards) - 1)))])        

    #end Setup methods

    #region Main Functions

    #   Gets the score for the player.
    def get_score(self, is_equivalent, is_ending_player):
        score = self.score
        rule = self.rule
        if rule is not None:
            if rule[1][0] != 100.0:
                score = score + 15
            if rule[1][1] != 100.0:
                score = score + 30
        else:
            score = score + 30
        if is_equivalent:
            score = score - 75
            if is_ending_player:
                score = score - 25
        return score
        
    #   This function will set the dealer rule using the
    #   helper functions in new_eleusis.py.
    #   TODO: Need to update a few things based on prof's suggestions.
    def set_rule(self, dealer_rule, player_rule):
        self.dealer_rule = new_eleusis.parse(dealer_rule)

    #   This function will return the current actual rule that the player is
    #   considering and will be used to determine the score.
    #   Returs the best rule in the list of rules
    def get_rule(self):
        if len(self.thinker.guessed_rules) > 0:
            self.rules = self.prioritize_rules(self.thinker.guessed_rules)
            self.rule = self.rules[-1]
            return self.rule
        return None
    
    #   This function will create the board state in string representation
    #   Returns string for the board
    def board_state(self):
        board = "{\n"
        for card in self.board:
            board = board + "\t {" + card[0] + "} , Incorrect Cards " + str(card[1]) + "\n"
        board = board.strip(" ").strip(",")
        board = board + "}"
        return board

    #   This function will play a card and determine if it satisfies the rule.
    #   This also updates the board_state.
    #   Returns true or false
    def play(self, card):
        if len(self.board) >= self.num_initial_cards:
            self.thinker.playNext(thinker.Card(card[:-1], card[-1]))
        if len(self.board) > 0:
            last_three = self.get_last_three(card, self.board, -1)
            if self.evaluate_card(last_three, self.thinker.dealer_rule):
                self.board.append((card, []))
                return True
            else:
                self.board[len(self.board) - 1][1].append(card)
                return False
        else:
            self.board.append((card, []))
            return True

    #   This function handles the player which will determine when and what to play
    #   and choosing when to declare success.
    def scientist(self):
        result = self.decide_success()
        card = self.get_best_card()
        if (result is not None) or len(self.thinker.history) >= max_plays:
            return result[0]
        correct = self.play(card)
        self.get_cards(1)
        history_len = len(self.thinker.history)
        if correct:        
            if history_len >= min_plays and history_len <= max_plays:        
                self.score = self.score + 1
        else:
            self.score = self.score + 2
        return card
      

    #end Main Functions



    #region Helper Functions


    # Evaluates a card with the provided rule.
    # Returns True or False.
    def evaluate_card(self, cards, rule):
        if rule.evaluate(cards):
            return True
        else:
            return False

    # Gets the last three cards from the board starting at an index
    # Passing -1 gives the -1, and -2 index if they exist
    def get_last_three(self, card, board, index):
        last_three = []
        if index == -1:
            if len(board) > 0:
                last_three.append(board[-1][0])
            else:
                last_three.insert(1, None)
            if len(board) < 2:
                last_three.insert(0, None)
            else:
                last_three.insert(0, board[-2][0])
        elif index == 0:
            return []
        else:
            if index >= 2:
                last_three.append(board[index - 2][0])
            else:
                last_three.append(None)
            last_three.append(board[index - 1][0])
        last_three.append(card)
        return last_three

    #   Based on the current possible rules, decides the best card to play.
    #   Applies constrainsts at this stage.
    #   Returns the card to play.
    def get_best_card(self):
        index = -1
        try:
            correct_indeces = []
            incorrect_indeces = []
            player_rule = new_eleusis.parse(self.rule[0])
            # for all the cards in the hand, assign correct or 
            #   incorrect against the player's current rule
            for i in range(0, len(self.hand)):
                last_three = self.get_last_three(self.hand[i], self.board, -1)
                if self.evaluate_card(last_three, player_rule):
                    correct_indeces.append(i)
                else:
                    incorrect_indeces.append(i)
            # if the last play made was a positive test, play a negative
            if self.last_play_positive:
                self.last_play_positive = False
                # if there are incorrect cards in the hand
                if len(incorrect_indeces) > 0:
                    index = incorrect_indeces[random.randint(0, len(incorrect_indeces) - 1)]
                    for i in range(0, len(incorrect_indeces)):
                        if self.hand[index] in self.board[-1][1]:
                            index = incorrect_indeces[random.randint(0, len(incorrect_indeces) - 1)]
                        else:
                            break
                    if self.hand[index] in self.board[-1][1]:
                        index = correct_indeces[random.randint(0, len(correct_indeces) - 1)]
                else:
                    index = correct_indeces[random.randint(0, len(correct_indeces) - 1)]
            else:
                self.last_play_positive = True
                 # if there are correct cards in the hand
                if len(correct_indeces) > 0:
                    index = correct_indeces[random.randint(0, len(correct_indeces) - 1)]
                else:
                    index = incorrect_indeces[random.randint(0, len(incorrect_indeces) - 1)]
        except:
            # if the rule evaluation fails
            index = -1
        
        #play the card with the corresponding index
        return self.get_card_from_hand(index)
    
    # Gets a random rule. Obtained from game.py from the TA's code.
    def generate_random_rule(self):
        # Generate a random rule
        rule = ""
        conditions = ["equal", "greater"]
        properties = ["suit", "value"]
        cond = conditions[random.randint(0, len(properties) - 1)]
        if cond == "greater":
            prop = "value"
        else:
            prop = properties[random.randint(0, len(properties) - 1)]

        rule += cond + "(" + prop + "(current), " + prop + "(previous)), "
        return rule[:-2]+")"

    #   Generates rules that apply to the current state of the board. 
    #   Only a decent amount will be chosen sicne there could be infinute possible rules.
    #   Applies constraints at this stage.
    #   TODO: Infer Rules
    def generate_rules(self):
        correct_rules = []
        return correct_rules


    #   Sets priority to all the rules that are being considered currently.
    #   Uses a list of rules that contain the attribute: evaluation
    #   Returns the sorted list of rules.
    def prioritize_rules(self, rules):
        evaluation = []
        for rule in rules:
            efficiency = 0.0
            equivalence = 0.0
            try:
                parsed_rule = new_eleusis.parse(rule)
                efficiency = self.get_efficiency(parsed_rule)
                equivalence = self.get_equivalence(parsed_rule)
                evaluation.append((rule, (efficiency, equivalence)))
            except:
                evaluation.append((rule, (efficiency, equivalence)))
        return sorted(evaluation, key = lambda tuple: (tuple[1][0], tuple[1][1], -(len(tuple[0]))))


    # Gets the efficiency of a provided rule for all the correct cards.
    def get_efficiency(self, rule):
        total = len(self.board)
        correct = self.num_initial_cards
        for index in range(0, total):
            if index >= self.num_initial_cards:
                last_three = self.get_last_three(self.board[index][0], self.board, index)
                if self.evaluate_card(last_three, rule):
                    correct = correct + 1
        return (correct / float(total)) * 100
    
    
    # Gets the logical equivalence of a provided rule for all the played cards.
    def get_equivalence(self, rule):
        total = len(self.thinker.history)
        match = self.num_initial_cards
        for index in range(0, len(self.board)):
            card = self.board[index][0]
            incorrect_cards = self.board[index][1]
            if index >= self.num_initial_cards:
                last_three = self.get_last_three(card, self.board, index)
                player = self.evaluate_card(last_three, rule)
                if player == True:
                    match = match + 1
            for incorrect in incorrect_cards:
                last_three = self.get_last_three(incorrect, self.board, index + 1)
                player = self.evaluate_card(last_three, rule)
                if player == False:
                    match = match + 1
        return (match / float(total)) * 100


    #   Calculates if the player should decide success
    #   Returns true or false depending on the player needing to decide
    def decide_success(self):
        # get the current rule and history
        current_rule = self.get_rule()
        history_length = len(self.thinker.history)
        self.confidence = 1
        # if there is a rule, evaluate it and see if we need to declare
        if not current_rule is None:
            try:
                # pars the rule and get the requireed info
                parsed_rule = new_eleusis.parse(current_rule[0])
                efficiency = current_rule[1][0]
                equivalence = current_rule[1][1]
                rule_length = len(current_rule[0])
                # get the factors of the min_plays that will be used in order to decide
                factor = [(i * min_plays) for i in range(1, 11)]
                #if there have been more than min plays
                if history_length >= min_plays:
                    # if the current rule has 100 efficiency and 100 equivalence
                    if efficiency == 100 and equivalence == 100:
                        # if the length of the rule is less than factor[i + 2] or 
                        #   the plays is some value with a factor[i]
                        for i in range(0, 11):
                            rule_length_limit = 0
                            factor_limit = 0
                            # if the index is less than 7
                            if i < 7:
                                factor_limit = factor[i + 2]
                                rule_length_limit = factor[i + 3]
                            elif i == 7:
                                factor_limit = factor[i + 1]
                                rule_length_limit = factor[i + 2]
                            elif i == 8:
                                factor_limit = factor[i + 1]
                                rule_length_limit = factor[i + 1]
                            else:
                                factor_limit = factor[i]
                                rule_length_limit = factor[i]
                            if rule_length <= rule_length_limit or history_length >= factor_limit:
                                self.confidence = self.confidence * 1.0
                                return current_rule
                    # if the current rule has 100 efficiency or 100 equivalence
                    elif efficiency == 100 or equivalence == 100:
                        # if the history is 
                        if history_length >= factor[2] and rule_length <= factor[4]:
                            self.confidence = self.confidence * 0.75
                            return current_rule
                        elif history_length >= factor[3]:
                            self.confidence = self.confidence * 0.50
                            return current_rule
                    # if the current rule is not as efficient as we like, show rule if max plays have been made
                    elif history_length >= max_plays:
                        self.confidence = self.confidence * 0.25
                        return current_rule
            except:
                self.confidence = self.confidence * 0.0
                if history_length >= max_plays:
                    return current_rule
        return None


    #   Builds the list of all possible cards
    def build_all_cards(self):
        for value in card_values:
            for suit in card_suits:
                self.all_cards.append(value + suit)


    #   Gets a to play from the hand
    #   Returns a card.
    def get_card_from_hand(self, index):
        if index < 0 or index > 13:
            #get a random card
            return self.hand.pop(int(round(random.random() * (len(self.hand) - 1))))
        else:
            #get a card from the index
            return self.hand.pop(index)

    #end Helper Functions

#end Scientist class


#region Adversary Class

# The following code was provided by the TAs and we have modified it to fit our program.

global game_ended
game_ended = False

def generate_random_card():
    values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    suits = ["S", "H", "D", "C"]
    return values[random.randint(0, len(values)-1)] + suits[random.randint(0, len(suits)-1)]

class Adversary(object):
    def __init__(self):
        self.hand = [generate_random_card() for i in range(14)]
        self.score = 0
        self.rule = self.generate_rule()

    def play(self, length):
        """
        'cards' is a list of three valid cards to be given by the dealer at the beginning of the game.
        Your scientist should play a card out of its given hand.
        """
        # Return a rule with a probability of 1/14
        prob_range = random.randint(min_plays * 2, min_plays * 3)
        prob_list = [i for i in range(prob_range)]
        prob = prob_list[random.randint(0, prob_range - 1)]
        if prob == 1 and length >= min_plays:
            return self.rule
        else:
            card = self.hand.pop(random.randint(0, len(self.hand) - 1))
            self.hand.append(generate_random_card())
            return card
    
    # Generates a random rule for the adversary.
    def generate_rule(self):
        # Generate a random rule
        rule = ""
        conditions = ["equal", "greater"]
        properties = ["suit", "value"]
        cond = conditions[random.randint(0, len(properties) - 1)]
        if cond == "greater":
            prop = "value"
        else:
            prop = properties[random.randint(0, len(properties) - 1)]

        rule += cond + "(" + prop + "(current), " + prop + "(previous)), "
        return rule[:-2]+")"

    # Updates the score for this adversary.
    def update_score(self, is_correct, length):
        if is_correct:  
            if length >= min_plays and length <= max_plays:              
                self.score = self.score + 1
        else:
            self.score = self.score + 2

#end Adversary Class


#call the main method
main(sys.argv)
