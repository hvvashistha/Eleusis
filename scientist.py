import random
import eleusis

# globals
card_values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
card_suits = ['C', 'D', 'H', 'S']
card_colors = {
    'C' : 'B',
    'D' : 'R',
    'H' : 'R',
    'S' : 'B'
}

class Scientist:

	def __init__(self, cards, rule):
		self.dealer_rule = None
		self.rules = []
		self.board = []
		self.total_moves = 0
		self.all_cards = []
		for card in cards:
			self.board.append((card, []))
		self.set_rule(rule)
		self.build_all_cards()


	#region Main Functions

	#	This function will set the dealer rule using the
	#	helper functions in new_eleusis.py.
	#	TODO: Need to update a few things based on prof's suggestions.
	def set_rule(self, expression):
		self.dealer_rule = eleusis.parse(expression)

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
	def play(self, card):
		self.total_moves = self.total_moves + 1
		last_three = []
		last_three.append(self.board[-1][0])
		if len(self.board) < 2:
			last_three.insert(0, None)
		else:
			last_three.insert(0, self.board[-2][0])
		last_three.append(card)
		if self.dealer_rule.evaluate(last_three):
			self.board.append((card, []))
			return True
		else:
			self.board[len(self.board) - 1][1].append(card)
			return False

	#	This function handles the player which will determine when and what to play
	#	and choosing when to declare success.
	def scientist(self):
		end = False
		# first move play at random
		self.play(self.get_random_card())
		print self.board_state()
		while not end:
			raw_input('Press enter to continue.')
			self.rules = self.generate_rules()
			self.play(self.get_best_card())
			print self.board_state()
			self.decide_success()
		print "Finished."

	#	Adds 1 for every right card, 2 for every wrong card, 15 for a wrong rule, 
	#		and 30 for a rule that does not satisfy the cards on the board.
	#	Returns a value for the score
	def score(self):
		score = 0
		current_rule = self.rule()
		for card in self.board:
			score = score + 1 + (2 * len(card[1]))
		if current_rule != self.dealer_rule:
			score = score + 15
		if not current_rule.evaluate(board):
			score = score + 30
		return score

	#end Main Functions


	#region Helper Functions

	#	Based on the current possible rules, decides the best card to play.
	#	Applies constrainsts at this stage.
	#	Returns the card to play.
	def get_best_card(self):
		# previous2 = None
		# previous = None
		# current = self.board[-1]
		# if len(self.board) > 2:
		# 	previous2 = self.board[-3]
		# elif len(self.board) > 1:
		# 	previous = self.board[-2]
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
		total = 0;
		correct = 0;
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


if __name__ == "__main__":
    sci = Scientist(["4H"], "even(current)")
    sci.scientist()