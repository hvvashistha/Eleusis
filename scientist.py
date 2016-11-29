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

def diff_suit(a, b):
    suita = eleusis.to_function["suit"](a)
    suitb = eleusis.to_function["suit"](b)
    # print "Calling diff_Suit"
    # print suita + " " + suitb
    return "CDHS".index(suita) - "CDHS".index(suitb)

def diff_value(a, b):
    valuea = eleusis.to_function["value"](a)
    valueb = eleusis.to_function["value"](b)
    # print "Calling diff_value "
    # print (valuea - valueb)
    return valuea - valueb

def current(c):
    # print "Current "+c
    return c

def prev1(c, p1):
    # print "prev1 "+c+" "+p1
    return p1

def prev2(c, p1, p2):
    # print "prev2 "+c+" "+p1+" "+p2
    return p2

functions = {
    'attribute': [prev2, prev1, current, eleusis.to_function['suit'], eleusis.to_function['is_royal'],
                eleusis.to_function['even'], eleusis.to_function['color'], eleusis.to_function['value'],
                diff_suit, diff_value],
    'comparative': [eleusis.to_function['equal'], eleusis.to_function['greater']],
    'logic': ['andf', 'orf', 'notf', 'iff'],
    'modifier': ['plus1', 'minus1']
}

class Scientist:

	def __init__(self, cards, rule):
		self.dealer_rule = None
		self.correct_list = []
		self.incorrect_list = []
		self.history = []
		self.rules = []
		self.board = []
		self.total_moves = 0
		self.all_cards = []
		self.truth_table = []
		for card in cards:
			self.board.append((card, []))
			self.history.append(card, True)
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
			self.history.append((card, True))
			return True
		else:
			self.board[len(self.board) - 1][1].append(card)
			self.history.append((card, False))
			return False

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
			self.recordPlay()
			print self.board_state()
			self.decompose(self.correct_list, self.incorrect_list)
			if self.decide_success() or count >= plays:
				end = True
			count = count + 1
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

	def recordPlay(self, correct):
		record = []
		if len(self.history) > 0:
			for f in functions['attribute']:
				try:
					record.append(f(str(history[-1])))
				except:
					try:
						record.append(f(str(history[-1]),str(history[-2])))
					except:
						record.append(f(str(history[-1]), str(history[-2]), str(history[-3])))
		self.truth_table.append(record)

	def decompose(self, correct_list, incorrect_list):
		final_rule = {}
		store_dec = [[0 for x in range(len(correct_list) - 1)] for y in range(10)]
		store_dec_2 = [[0 for x in range(len(correct_list) - 1)] for y in range(10)]
		visibility = [[0 for x in range(7)] for y in range(7)]

		# INITIALIZING DICTIONARIES TO STORE THE ATTRIBUTES OF NEXT CORRECT
		# ENTRIES FOR EVERY ATTRIBUTE
		for j in range(3,10):
			store_dec[j] = {}
			for i in range(len(correct_list) - 1):
				store_dec[j][correct_list[i][j]] = []
		for j in range(3,10):
			store_dec_2[j] = {}
			for i in range(len(correct_list) - 1):
				store_dec_2[j][correct_list[i][j]] = []
		# OUTER LOOP TO TRAVERSE THROUGH ALL THE ATTRIBUTES
		for j in range(3,10):
			# THIS LOOP TO TRAVERSE THROUGH ALL THE CORRECT ENTRIES
			# THIS STORES THE NEXT CORRECT ENTRY PERTAINING TO EACH ATTRIBUTE
			# OF THE CURRENT NEXT ENTRY
			for i in range(len(correct_list) - 1):
				#print correct_list[i][j]
				store_dec[j][correct_list[i][j]].append(correct_list[i + 1])
				#print
				#"store_dec[",functions['attribute'][j].__name__,"][",correct_list[i][j],"]
				#: ",store_dec[j][correct_list[i][j]]
			#print
			#"***********************************************************************************"

		for j in range(3,10):
			for k,v in store_dec[j].iteritems():
				for x in range(3,10):
					l = set()
					#print len(v)
					for z in v:
						l.add(z[x])
					store_dec_2[j][k].append(l)
				


		for j in range(3,10):
			attr_suit = []
			attr_isroyal = []
			attr_even = []
			attr_color = []
			attr_value = []
			attr_diff_suit = []
			attr_diff_value = []
			for k,v in store_dec_2[j].iteritems():
				# print store_dec_2[j].keys().index(k)
				# print "J : ",j
				# print "K : ",k
				# print "V : ",v
				# print "___________________________________________"
				if(attr_suit == []):
					attr_suit = v[0]
				else:
					# print "Suit Intersection : ",v[0].intersection(attr_suit)
					if len(v[0].intersection(attr_suit)) == 0:
						attr_suit = attr_suit.union(v[0])
						# print "Suit Union : ",attr_suit
					elif len(v[0].intersection(attr_suit)) > 0:
						visibility[j - 3][0] = 1
						
				
				#------------------------------------------------------------------------------------------
				if(attr_isroyal == []):
					attr_isroyal = v[1]
				else:
					# print "IsRoyal Intersection :
					# ",v[1].intersection(attr_isroyal)
					if len(v[1].intersection(attr_isroyal)) == 0:
						attr_isroyal = attr_isroyal.union(v[1])
						# print "isRoyal Union : ",attr_isroyal
					elif len(v[1].intersection(attr_isroyal)) > 0:
						visibility[j - 3][1] = 1
						
				
				#------------------------------------------------------------------------------------------
				if(attr_even == []):
					attr_even = v[2]
				else:
					# print "Even Intersection : ",v[2].intersection(attr_even)
					if len(v[2].intersection(attr_even)) == 0:
						attr_even = attr_even.union(v[2])
						# print "Even Union : ",attr_even
					elif len(v[2].intersection(attr_even)) > 0:
						visibility[j - 3][2] = 1
						
				
				#------------------------------------------------------------------------------------------
				if(attr_color == []):
					attr_color = v[3]
				else:
					# print "Color Intersection :
					# ",v[3].intersection(attr_color)
					if len(v[3].intersection(attr_color)) == 0:
						attr_color = attr_color.union(v[3])
						# print "Color Union : ",attr_color
					elif len(v[3].intersection(attr_color)) > 0:
						visibility[j - 3][3] = 1
						

				#------------------------------------------------------------------------------------------
				if(attr_value == []):
					attr_value = v[4]
				else:
					# print "Value Intersection :
					# ",v[4].intersection(attr_value)
					if len(v[4].intersection(attr_value)) == 0:
						attr_value = attr_value.union(v[4])
						# print "Value Union : ",attr_value
					elif len(v[4].intersection(attr_value)) > 0:
						visibility[j - 3][4] = 1
						
				
				#------------------------------------------------------------------------------------------
				if(attr_diff_suit == []):
					attr_diff_suit = v[5]
				else:
					# print "Diff Suit Intersection :
					# ",v[5].intersection(attr_diff_suit)
					if len(v[5].intersection(attr_diff_suit)) == 0:
						attr_diff_suit = attr_diff_suit.union(v[5])
						# print "Diff Suit Union : ",attr_diff_suit
					elif len(v[5].intersection(attr_diff_suit)) > 0:
						visibility[j - 3][5] = 1
						
				
				#------------------------------------------------------------------------------------------
				if(attr_diff_value == []):
					attr_diff_value = v[6]
				else:
					# print "Diff Value Intersection :
					# ",v[6].intersection(attr_diff_value)
					if len(v[6].intersection(attr_diff_value)) == 0:
						attr_diff_value = attr_diff_value.union(v[6])
						# print "Diff value Union : ",attr_diff_value
					elif len(v[6].intersection(attr_diff_value)) > 0:
						visibility[j - 3][6] = 1
		
		min = 900000  
		min_x = 0  
		min_x_index = 0
		print visibility
		for x1 in visibility:
			count = 0
			for y1 in x1:
				if y1 == 1:
					count = count + 1
				if(count < min):
					min = count
					min_x = x1
					min_x_index = visibility.index(x1)
		

		# # print min_x
		# # print min_x_index

		

		# for k1,v1 in store_dec_2[min_x_index + 3].iteritems():
		# 	#print k1
		# 	var_attribute = functions['attribute'][min_x_index + 3].__name__
		# 	new_key = var_attribute + "_" + str(k1)
		# 	# print new_key
		# 	# print type(new_key)
		# 	final_rule[new_key] = []
		# 	for i2 in range(len(v1)):
		# 		if min_x[i2] == 0:
		# 			final_rule[new_key].append(functions['attribute'][i2 + 3].__name__ + "_" + str(v1[i2]))
		# print final_rule


	#end Helper Functions


if __name__ == "__main__":
    sci = Scientist(["4H"], "even(current)")
    sci.scientist(100)
