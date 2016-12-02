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

# START ###############################################################################################################################################

#Language: Extended Propositional
class Language:
    def __init__(self):
        self.complex = []

    def addComplex(self, complexS):
        self.complex.append(complexS)

    def dnf(self):
        return self.complex

    def updateDnf(self, dnf):
        self.complex = dnf

Language.ATTRIBUTE = "ATTRIBUTE"
Language.CONSTANT = "CONSTANT"

# VL1 representation
# Class Entity represents an entity, an entity records the attributes an object of that entity is can have and their respective domains
class Selector:
    def __init__(self, variableIdentity, variableType, variableDomain, relation, reference, spID = ''):
        # relation : '==', '>', '>=', '<', '<=', '!='
        self.variable = (variableIdentity, variableType, variableDomain)
        self.specialIdentifier = spID
        self.relation = relation
        self.reference = reference

    def __str__(self):
        ref = ''
        if isinstance(self.reference, list):
            ref = ''
            for i in self.reference:
                ref = ref + (str(i) if not isinstance(i, tuple) else (str(i[0]) + ".." + str(i[1]))) + ","
            ref = ref[:-1]
        else:
            ref = str(self.reference)

        return "[" + str(self.variable[0] + self.specialIdentifier) + " " + self.relation + " {" + str(ref) + "}]"

    def __cmp__(self, sel):
        if self.variable == sel.variable:
            return cmp(self.getExpandedReference(), sel.getExpandedReference())
        return False

    def getIdentifier(self):
        return self.variable[0]

    def getName(self):
        return self.variable[0] + self.specialIdentifier

    def getSPID(self):
        return self.specialIdentifier

    def getReference(self):
        return self.reference

    def getExpandedReference(self):
        ref = self.getReference()
        if isinstance(ref, list):
            fullRef = []
            for i in ref:
                if isinstance(i, tuple):
                    fullRef = fullRef + [j for j in range(i[0], i[1]+1)]
                else:
                    fullRef.append(i)
            return fullRef
        return [ref]

    def getDomain(self):
        return self.variable[2]

    def getExpandedDomain(self):
        if self.variable[1] == Selector.INTERVAL and isinstance(self.getDomain()[0], tuple):
            return [i for i in range(self.getDomain()[0][0], self.getDomain()[0][1] + 1)]
        return self.getDomain()

    def getType(self):
        return self.variable[1]

    def setSPID(self, spID = ''):
        self.specialIdentifier = str(spID)

    def setReference(self, reference):
        self.reference = reference
        self.reference.sort()

    def setRelation(self, rel):
        self.relation = rel

    def test(self, value, strict=False):
        if isinstance(value, Selector):
            value = value.getExpandedReference()
        ref = self.getExpandedReference()
        if isinstance(ref, list):
            sRef = set(ref)
            sVal = set(value if isinstance(value, list) else [value])
            if strict:
                return sRef == sVal
            else:
                return sRef.issuperset(sVal)
        return eval("'" + str(value) + "'" + self.relation + "'" + str(ref) + "'")

    def difference(self, sel):
        assert self.variable == sel.variable
        name = ('d' + self.variable[0] + self.specialIdentifier + sel.specialIdentifier)
        if self.variable[1] == Selector.NOMINAL:
            return Selector(name, Selector.INTERVAL, [0, 1], '==',
                1 if self.reference != sel.reference else 0)
        elif self.variable[1] == Selector.CIRCULAR:
            dLimit = len(self.variable[2]) - 1
            return Selector(name, Selector.INTERVAL, [(-dLimit, dLimit)], '==',
                self.variable[2].index(self.reference) - sel.variable[2].index(sel.reference))
            # return len(self.variable[2]) % (self.variable[2].index(self.reference) - sel.variable[2].index(sel.reference))
        else:
            dLimit = self.variable[2][0][1] - self.variable[2][0][0]
            return Selector(name, Selector.INTERVAL, [(-dLimit, dLimit)], '==',
                self.reference - sel.reference)



#Attribute Types
Selector.NOMINAL = "NOMINAL"
Selector.CIRCULAR = "CIRCULAR"
Selector.INTERVAL = "INTERVAL"

def setToRange(rangeSet):
    r = []
    for i in rangeSet:
        if isinstance(i, tuple):
            r = r + range(i[0], i[1]+1)
        else:
            r.append(i)
    return r

class Operator:
    def __init__(self, operator, paramSize = 1):
        if type(operator) == type(self.noop):
            self.op = operator
        else:
            operator = self.noop

        self.paramSize = paramSize

    def test(self, *args):
        return self.op(*args)

    def noop(self):
        return None

class Formula:
    def __init__(self, operator, entity, attributes, attributeTypes):
        assert isinstance(operator, Operator)
        assert isinstance(attributes, list)
        assert len(attributes) == operator.paramSize
        assert isinstance(attributeTypes, list)
        assert len(attributeTypes) == operator.paramSize
        self.operator = operator
        self.attributes = attributes
        self.types = attributeTypes

# END #################################################################################################################################################

class Card:
    def __init__(self, value, suit):
        if not isinstance(value, int):
            value = int(eleusis.value_to_number(value))

        # if not Card.definition.inDomain("value", value) or not Card.definition.inDomain("suit", suit):
        #     print 'Wrong Values'
        #     raise Exception('Wrong Values')
        self.value = Selector("value", Selector.INTERVAL, Card.domain["value"], '==', value)
        self.suit = Selector("suit", Selector.CIRCULAR, Card.domain["suit"], '==', suit)
        self.color = Selector("color", Selector.NOMINAL, Card.domain["color"], '==', Card.color[suit])

    def __str__(self):
        return str(self.value.getReference()) + str(self.suit.getReference())

    def __cmp__(self, other):
        if isinstance(other, Card):
            return self.value.getReference() == other.value.getReference() and self.suit.getReference() == other.suit.getReference()
        return False

    def __iter__(self):
        yield self.value
        yield self.suit
        yield self.color

Card.domain = {
    "value": [(1,13)],
    "suit": ['C', 'D', 'H', 'S'],
    "color": ['B', 'R']
}
Card.color = {
    'C': 'B',
    'D': 'R',
    'H': 'R',
    'S': 'B'
}

class Deck:
    def __init__(self, deckMultiples = 1):
        self.deck = []
        deck = []
        for suit in Card.domain["suit"]:
            for value in setToRange(Card.domain["value"]):
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

def colored(string, color):
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    return eval(color.upper()) + str(string) + ENDC

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
        self.playRun = 1
        if rule is not None:
            self.ruleTree = eleusis.parse(rule)

        self.recordPlay([godPlay], True)

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
            # print "Penalty cards : " + str(len(cards))
            return cards
        return correct

    def recordPlay(self, lastPlays, correct):
        new_record = []
        if len(self.history) > 0:
            for f in functions['attribute']:
                try:
                    new_record.append(f(str(lastPlays[2])))
                except:
                    try:
                        new_record.append(f(str(lastPlays[2]),str(lastPlays[1])))
                    except:
                        new_record.append(f(str(lastPlays[2]),str(lastPlays[1]), str(lastPlays[0])))

            self.truthTable.append(new_record)
        self.history.append((lastPlays[-1], correct))

    def printRecord(self, recordSize=0):
        for record in self.history[-recordSize:]:
            print colored(record[0], 'green' if record[1] else 'red') + ' |',
        print ''


        # for f in functions['attribute']:
        #     print f.__name__ + ' |',
        # print "correct"
        # for record in self.truthTable:
        #     index = self.truthTable.index(record)
        #     for attribute in record:
        #         print colored(str(attribute) + '\t|', 'green' if self.history[index + 1][1] else 'red'),
        #     print str(self.history[index + 1][1])
        # sys.stdout.write('\010\010\n\n')


    def playNext(self, runCount = None):
        player = self.nextPlayer()
        play = None
        card = None
        # os.system('clear')
        # self.printRecord()
        lastPlays = []
        events = []
        if self.randomPlay:
            play = player.playRandom()
        else:
            # print "Player " + str(self.players.index(player) + 1) + " : "
            player.showCards()

            while card is None:
                ri = raw_input('Choose Card : ')
                ri = ri.upper()
                try:
                    card = Card(ri[:-1], ri[len(ri)-1:])
                except:
                    pass
            play = player.playCard(card)

        # print "Player " + str(self.players.index(player) + 1) + " : " + str(play)

        if self.ruleTree is None:
            correct = True if raw_input('Correct? (y/n) : ') == 'y' else False
        else:
            historyLen = len(self.history) - 1

            for i in range(historyLen, -1, -1):
                if self.history[i][1]:
                    events.insert(0, copy.deepcopy(self.history[i][0]))
                    lastPlays.insert(0, str(self.history[i][0]))
                if len(lastPlays) >= 2:
                    break
            events.append(copy.deepcopy(play))
            lastPlays.append(str(play))
            while len(lastPlays) < 3:
                events.insert(0, None)
                lastPlays.insert(0, None)

            correct = self.ruleTree.evaluate(lastPlays)

        nextPlay = []

        if play is None or self.callPlay(player, correct) is None:
            return nextPlay

        self.recordPlay(events, correct)
        # raw_input()
        # os.system('clear')
        # self.printRecord()
        if self.randomPlay and (runCount is None or self.playRun < runCount):
            self.playRun = self.playRun + 1
            nextPlay = self.playNext(runCount = runCount)
        else:
            self.playRun = 1

        return [(events, correct)] + nextPlay

if __name__ == "__main__":
    game = Game(Card(sys.argv[1][:-1], sys.argv[1][len(sys.argv[1])-1:]), rule=sys.argv[2], randomPlay = True)
    game.playNext()
