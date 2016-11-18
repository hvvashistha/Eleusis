import eleusis

class Scientist:

	def __init__(self, cards, rule):
		self.dealer_rule = None
		self.rules = []
		self.board = []

	def start(self):
		counter = 0
		

	#region Main Functions

	#	This function will set the dealer rule using the
	#	helper functions in new_eleusis.py
	def set_rule(self, expression):
		self.dealer_rule = eleusis.tree(expression)

	# 	This function will return the current actual rule that the player is
	#	considering and will be used to determine the score
	def rule(self):
		if len(self.rules) > 0:
			return self.prioritize_rules(rules)[0]
		return None
	
	#	This function will display the board state in string representation
	def board_state(self):
		board = "{"
		for card in self.board:
			board = board + "(" + card[0] + ", " + str(card[1]) + ")"
			board = board + "}"
		return board

	#	This function will play a card and determine if it satisfies the rule
	#	This also updates the board_state
	def play(self, card):
		if self.dealer_rule.evaluate(card):
			self.board.append((card, []))
			return True
		else:
			self.board[len(self.board) - 1][1].append(card)
			return False

	#	This function handles the player which will determine when and what to play
	#	and choosing when to declare success
	def scientist(self, counter):
		end = False
		while not end:
			print "HELLO"
			end = True

	#	Returns the score of the game
	def score(self):
		score = 0
		current_rule = self.rule()
		for card in self.board:
			score = score + 1
			score = score + (2 * len(card[1]))
		if current_rule != self.dealer_rule:
			score = score + 15
		if not current_rule.evaluate(board):
			score = score + 30
		return score

	#end Main Functions


	#region Helper Functions
	
	#	Sets priority to all the rules that are being considered currently.
	#	Uses a list of rules that contain the attribute: evaluation
	#	Returns the sorted list of rules.
	def prioritize_rules(self):
		for rule in rules:
			rule.evaluation = self.evaluate_rule(rule)
		return sort(rules)

	#	Evaluates a rule based on how many correct and wrong cards it produced
	def evaluate_rule(self, rule):
		total = 0;
		correct = 0;
		for card in self.board:
			total = total + 1
			if rule.evaluate(card):
				correct = correct + 1
		return (correct / total) * 100

	#	Calculates if the player should decide success
	def decide_success(self):
		current_rule = self.rule()
		if len(self.board) > 20 and current_rule.evaluate(board):
			if rule.evaluation == 100 or len(self.board) > 200:
				return True
			return False
		return False