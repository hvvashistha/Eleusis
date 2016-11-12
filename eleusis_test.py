# -*- coding: utf-8 -*-

import sys
import os
import copy
import random
import pdb
import eleusis

"""
    •   suit(card) — returns the suit of a card, as a single letter: C, D, H, or S for Clubs, Diamonds, Hearts, or Spades
    •   color(card) — returns the color of a card, as a single letter: B for black, R for red
    •   value(card) — returns the integer value of a card, from 1 (Ace) to 13 (King)
    •   is_royal(card) — returns True if the card is a Jack, Queen, or King
    •   equal(a, b) — tests if two cards, suits, colors, or values are equal
    •   less(a, b) — tests if a < b; cards are compared first by suit, C < D < H < S, then if suits are equal, by value; for colors, B < R
    •   greater(a, b) — same as less(b, a)
    •   plus1(x) — returns the next higher value, suit, or card in a suit; error if there is none higher
    •   minus(x) — returns the next lower value, suit, or card in a suit; error if there is none lower
    •   even(card) — tests if the cards numeric value is even
    •   odd(card) — tests if the cards numeric value is odd
    •   andf(a, b) — True if both a and b are true
    •   orf(a, b) — True if either or both a and b are true
    •   notf(a) — True if a is False
    •   iff(test, a, b) — if the test is True, evaluate and return a, else evaluate and return b
"""

def diff_suit(a, b):
    suita = eleusis.to_function["suit"](a)
    suitb = eleusis.to_function["suit"](b)
    print suita + " " + suitb
    return "CDHS".index(suita) - "CDHS".index(suitb)

def diff_value(a, b):
    valuea = eleusis.to_function["value"](a)
    valueb = eleusis.to_function["value"](b)
    return valuea - valueb

def current(c):
    return c

def prev1(c, p1):
    return p1

def prev2(c, p1, p2):
    return p2

functions = {
    'attribute': [prev2, prev1, current, eleusis.to_function['suit'], eleusis.to_function['is_royal'],
                eleusis.to_function['even'], eleusis.to_function['color'], eleusis.to_function['value'],
                diff_suit, diff_value],
    'comparative': [eleusis.to_function['equal'], eleusis.to_function['greater']],
    'logic': ['andf', 'orf', 'notf', 'iff'],
    'modifier': ['plus1', 'minus1']
    }

def colored(string, color):
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    return eval(color.upper()) + str(string) + ENDC

class Card:
    def __init__(self, value, suit):
        if isinstance(value, int):
            value = eleusis.value_to_number(value)

        if not value in Card.values or not suit in Card.suit:
            print 'Wrong Values'
            raise Exception('Wrong Values')

        self.card = value + suit

    def __str__(self):
        return self.card

    def __cmp__(self, other):
        if isinstance(other, Card):
            return cmp(self.card, other.card)
        return False

Card.values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
Card.suit = ['C', 'D', 'H', 'S']
Card.suitColors = {
    'C' : 'B',
    'D' : 'R',
    'H' : 'R',
    'S' : 'B'
}

class Deck:
    def __init__(self, deckMultiples = 1):
        self.deck = []
        deck = []
        for suit in Card.suit:
            for value in Card.values:
                deck.append(Card(value, suit))

        for i in range(0, deckMultiples):
            self.deck.extend(copy.deepcopy(deck))

    def shuffle(self):
        random.shuffle(self.deck)

    def drawCards(self, numberOfCards = 1):
        if len(self.deck) < numberOfCards:
            return None

        draw = []
        for i in range(0, numberOfCards):
            draw.append(self.deck.pop())
        return draw

    def drawCard(self, card):
        try:
            return self.deck.pop(self.deck.index(card))
        except:
            return None

    def __str__(self):
        return str(self.deck)

class Player:
    def __init__(self):
        self.cards = []

    def addCards(self, cards):
        if cards is not None:
            self.cards.extend(copy.deepcopy(cards))

    def playCard(self, card):
        try:
            return self.cards.pop(self.cards.index(card))
        except:
            return None

    def playRandom(self):
        try:
            return self.cards.pop(int(round(random.random() * (len(self.cards) - 1))))
        except:
            return None

    def showCards(self):
        for card in self.cards:
            print str(card) + ", ",
        sys.stdout.write('\010\010\n')

class Game:
    def __init__(self, godPlay, players = 6, randomPlay = False, rule = None):
        self.deck = Deck(6)
        self.history = []
        self.deck.shuffle()
        self.players = []
        self.truthTable = []
        self.playCounter = -1
        self.randomPlay = randomPlay
        self.ruleTree = None
        if rule is not None:
            self.ruleTree = eleusis.parse(rule)

        self.recordPlay([str(godPlay)], True)

        for i in range(0, players):
            player = Player()
            player.addCards(self.deck.drawCards(8))
            self.players.append(player)

    def nextPlayer(self):
        self.playCounter = (self.playCounter + 1) % len(self.players)
        return self.players[self.playCounter]

    def callPlay(self, player, correct = True):
        if not correct:
            cards = self.deck.drawCards(5)
            if cards is None or len(cards) < 5:
                return None
            player.addCards(cards)
            print "Penalty cards : " + str(len(cards))
            return cards
        return correct

    def recordPlay(self, lastPlays, correct):
        new_record = []
        if len(self.history) > 0:
            for f in functions['attribute']:
                try:
                    new_record.append(f(lastPlays[2]))
                except:
                    try:
                        new_record.append(f(lastPlays[2],lastPlays[1]))
                    except:
                        new_record.append(f(lastPlays[2],lastPlays[1], lastPlays[0]))

            self.truthTable.append(new_record)
        self.history.append((lastPlays[-1], correct))

    def printRecord(self):
        for record in self.history:
            print colored(record[0], 'green' if record[1] else 'red') + ' |',
        print ''


        for f in functions['attribute']:
            print f.__name__ + ' |',
        print "correct"
        for record in self.truthTable:
            index = self.truthTable.index(record)
            for attribute in record:
                print colored(str(attribute) + '\t|', 'green' if self.history[index + 1][1] else 'red'),
            print str(self.history[index + 1][1])
        sys.stdout.write('\010\010\n\n')


    def playNext(self):
        player = self.nextPlayer()
        play = None
        card = None
        os.system('clear')
        self.printRecord()
        lastPlays = []
        if self.randomPlay:
            play = player.playRandom()
        else:
            print "Player " + str(self.players.index(player) + 1) + " : "
            player.showCards()

            while card is None:
                ri = raw_input('Choose Card : ')
                ri = ri.upper()
                try:
                    card = Card(ri[:-1], ri[len(ri)-1:])
                except:
                    pass
            play = player.playCard(card)

        print "Player " + str(self.players.index(player) + 1) + " : " + str(play)

        if self.ruleTree is None:
            correct = True if raw_input('Correct? (y/n) : ') == 'y' else False
        else:
            historyLen = len(self.history) - 1

            for i in range(historyLen, -1, -1):
                if self.history[i][1]:
                    lastPlays.insert(0, str(self.history[i][0]))
                if len(lastPlays) >= 2:
                    break
            lastPlays.append(str(play))
            while len(lastPlays) < 3:
                lastPlays.insert(0, None)

            # pdb.set_trace()

            correct = self.ruleTree.evaluate(lastPlays)

        if play is None or self.callPlay(player, correct) is None:
            return "Game Stops"

        self.recordPlay(lastPlays, correct)
        # raw_input()
        os.system('clear')
        self.printRecord()
        self.playNext()

if __name__ == "__main__":
    game = Game(Card(sys.argv[1][:-1], sys.argv[1][len(sys.argv[1])-1:]), rule=sys.argv[2], randomPlay = True)
    game.playNext()
