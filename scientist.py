# -*- coding: utf-8 -*-

import random
import eleusis
import eleusis_test

# globals
card_values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
card_suits = ['C', 'D', 'H', 'S']
card_colors = {
    'C' : 'B',
    'D' : 'R',
    'H' : 'R',
    'S' : 'B'
}

# This class has a few player functions that are not used in phase 1
# But this is also used to score the player and end the game for phase 1

class Scientist:

	def __init__(self, cards, dealer_rule, player_rule):
		self.dealer_rule = None
		self.dealer_rule_str = dealer_rule
		self.player_rule = None
		self.player_rule_str = player_rule
		self.board = []
		self.total_moves = 0
		self.all_cards = []
		self.set_rule(dealer_rule, player_rule)
		self.build_all_cards()
		for card in cards:
			self.play(str(card[0]), self.dealer_rule)
		print "The Board state at the end is: "
		print self.board_state()

	#region Main Functions

	#	This function will set the dealer rule using the
	#	helper functions in new_eleusis.py.
	#	TODO: Need to update a few things based on prof's suggestions.
	def set_rule(self, dealer_rule, player_rule):
		self.dealer_rule = eleusis.parse(dealer_rule)
		self.player_rule = eleusis.parse(player_rule)

	# 	This function will return the current actual rule that the player is
	#	considering and will be used to determine the score.
	#	Returs the best rule in the list of rules
	def rule(self):
		if len(self.rules) > 0:
			return self.prioritize_rules(self.rules)[0]
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
	def play(self, card, rule):
		self.total_moves = self.total_moves + 1
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
		if len(self.board) > 0:
			if rule.evaluate(last_three):
				self.board.append((card, []))
				return True
			else:
				self.board[len(self.board) - 1][1].append(card)
				return False
		else:
			self.board.append((card, []))

	#	This function handles the player which will determine when and what to play
	#	and choosing when to declare success.
	def scientist(self, plays):
		end = False
		# first move play at random
		self.play(self.get_random_card())
		print self.board_state()
		count = 0
		while not end:
			#raw_input('Press enter to continue.')
			self.play(self.get_best_card())
			print self.board_state()
			if self.decide_success() or count >= plays:
				end = True
			count = count + 1
		print "Finished."

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
		print self.board_state()
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

	#	Based on the current possible rules, decides the best card to play.
	#	Applies constrainsts at this stage.
	#	Returns the card to play.
	def get_best_card(self):
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
		for rule in rules:
			rule.evaluation = self.evaluate_rule(rule)
		return sort(rules)

	#	Evaluates a rule based on how many correct and wrong cards it produced
	#	Returns the value for the evaluation (0 - 100)
	def evaluate_rule(self, rule):
		total = 0
		correct = 0
		for card in self.board:
			total = total + 1
			if rule.evaluate(card):
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

	#	Gets a random card to play from the whole deck.
	#	Returns a card.
	def get_random_card(self):
		return self.all_cards[int(round(random.random() * (len(self.all_cards) - 1)))]

	#end Helper Functions