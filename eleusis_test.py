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
    print "Inside Selector Class"
    def __init__(self, variableIdentity, variableType, variableDomain, relation, reference, spID = ''):
        # relation : '==', '>', '>=', '<', '<=', '!='
        self.variable = (variableIdentity, variableType, variableDomain)
        self.specialIdentifier = spID
        self.relation = relation
        self.reference = reference

    def __str__(self):
        ref = ''
        if self.variable[1] == Selector.NOMINAL:
            ref = ref.join(self.reference)
        elif isinstance(self.reference, list):
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
        return ref

    def getDomain(self):
        return self.variable[2]

    def getExpandedDomain(self):
        if self.variable[1] == Selector.INTERVAL and isinstance(self.variable[2], tuple):
            return [i for i in range(self.getDomain()[0], self.getDomain()[1] + 1)]
        return self.getDomain()

    def getType(self):
        return self.variable[1]

    def setSPID(self, spID = ''):
        self.specialIdentifier = str(spID)

    def setReferece(self, reference):
        self.reference = reference

    def setRelation(self, rel):
        self.relation = rel

    def test(self, value):
        if isinstance(value, Selector):
            value = value.getReference()
        ref = self.getExpandedReference()
        if isinstance(ref, list):
            return value in ref
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
        print "Calling Selector"
        str(self.value)
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
    def __init__(self, godPlay, players = 10, randomPlay = False, rule = None):
        self.deck = Deck(6)
        self.history = []
        self.deck.shuffle()
        self.players = []
        self.truthTable = []
        self.playCounter = -1
        self.randomPlay = randomPlay
        self.ruleTree = None
        self.playRun = 0
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
            print "Penalty cards : " + str(len(cards))
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

    def printRecord(self):
        for record in self.history:
            print colored(record[0], 'green' if record[1] else 'red') + ' |',
        print ''


        correct_list = [];
        incorrect_list = [];

      
        for f in functions['attribute']:
            #print "Fishy here"
            print f.__name__ + '|',
        print "correct"
        #print self.truthTable
        for record in self.truthTable:
            index = self.truthTable.index(record)
            if str(self.history[index + 1][1])=="True":
                correct_list.append(record)
            else:   
                incorrect_list.append(record)
            

               
            for attribute in record:
                #print type(record)
                
                print colored(str(attribute) + '\t|', 'green' if self.history[index + 1][1] else 'red'),
    
            
            print str(self.history[index + 1][1])
            #print "Correct List : ", correct_list;
            #print "Incorrect List : ", incorrect_list;
        sys.stdout.write('\010\010\n\n')
        #self.det_periodicity(correct_list,incorrect_list);
        self.det_decomposition(correct_list,incorrect_list)

    def det_decomposition(self,correct_list,incorrect_list):
        print "Decomposition Algorithm"

        store_dec = [[0 for x in range(len(correct_list)-1)] for y in range(10)];
        store_dec_2 = [[0 for x in range(len(correct_list)-1)] for y in range(10)];

        # INITIALIZING DICTIONARIES TO STORE THE ATTRIBUTES OF NEXT CORRECT ENTRIES FOR EVERY ATTRIBUTE
        for j in range(3,10):
            store_dec[j] = {};
            for i in range(len(correct_list)-1):
                store_dec[j][correct_list[i][j]] = [];
        for j in range(3,10):
            store_dec_2[j] = {};
            for i in range(len(correct_list)-1):
                store_dec_2[j][correct_list[i][j]] = [];
            
        # OUTER LOOP TO TRAVERSE THROUGH ALL THE ATTRIBUTES
        for j in range(3,10):
            # THIS LOOP TO TRAVERSE THROUGH ALL THE CORRECT ENTRIES 
            # THIS STORES THE NEXT CORRECT ENTRY PERTAINING TO EACH ATTRIBUTE OF THE CURRENT NEXT ENTRY
            for i in range(len(correct_list)-1):
                #print correct_list[i][j];
                store_dec[j][correct_list[i][j]].append(correct_list[i+1]);
                #print "store_dec[",functions['attribute'][j].__name__,"][",correct_list[i][j],"] :  ",store_dec[j][correct_list[i][j]];
            #print "***********************************************************************************"

        for j in range(3,10):
            for k,v in store_dec[j].iteritems():
                for x in range(3,10):
                    l = set();
                    #print len(v);
                    for z in v:
                        l.add(z[x])
                    store_dec_2[j][k].append(l);
                
        for j in range(3,10):
            union = []
            row = 0
            col = 0
            dict_items = store_dec_2[j].items()
            end = False
            print "Dictionary" + str(dict_items)
            print "Dictionary length: " + str(len(dict_items))
            while row < len(dict_items):
                k, v = dict_items[0]
                print k
                print v
                intersection = v[col].intersection(union);
                print intersection
                if len(intersection) == 0:
                    union = v[col].union(union);
                else:
                    union = []
                    row = 0
                    col = col + 1
                row = row + 1

                               
        # for j in range(3,10):
        #     for k,v in store_dec_2[j].iteritems():
        #         print k;
        #         for m in range(len(v)):
        #             print v[m];
        #         print "----------------------"
        #     print "____________________________________________________________________________________________________________"

            #     print store_dec_2[j][k];
            # print "**********************************************************************************************************"
        #print store_dec;

            # for i1 in store_dec:
            #     print i1;
            # print "---------------------------------------------------"


        # cond = False;
        # i = -1;
        # list_of_incorrect_after_every_correct = [[] for y in range(len(correct_list))] ;
        # for record in self.truthTable:
        #     index = self.truthTable.index(record)
        #     if (str(self.history[index + 1][1])=="True"):
        #         i = i + 1;

        #         cond = True;
        #         #print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        #         #print record;
        #         list_of_incorrect_after_every_correct[i].append(record);
        #         #print cond;
        #     else:
        #         if cond:  
        #             list_of_incorrect_after_every_correct[i].append(record);

        # for x in list_of_incorrect_after_every_correct:
        #     print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        #     print x;

        # for x in range(0,len(list_of_incorrect_after_every_correct)):
        #     print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
        #     if(len(list_of_incorrect_after_every_correct[x])>1):
        #         for z in range(len(list_of_incorrect_after_every_correct[x][0])):
        #             print list_of_incorrect_after_every_correct[x][0][z];

        #             for y in range(1,len(list_of_incorrect_after_every_correct[x])):
        #                 print list_of_incorrect_after_every_correct[x][y];


                    
    def det_periodicity(self,correct_list,incorrect_list):
        lenG = (len(correct_list)+len(incorrect_list))/2;
        #print lenG;
        
        w, h = lenG,10; 
        
        
        count = [[0 for x in range(10)] for y in range(lenG+1)] 
        count2 = [[0 for x in range(10)] for y in range(lenG+1)] 


        max = -10000000000;
        var_1 =  set();
        var_2 = -1;
        var_3 = -1;
        var_4 = -1;
        maxe = -10000000000;
        

        #print "Determining Correct Periodicity";
        for a in range(lenG,0,-1):
            #print "==============================================================================================================================================================="
            #print "Tuple Length " , a;
            for j in range(2,10):
            
                #print "***************************************************************************************************************************************************************"
                #print correct_list[i];
                #print correct_list[i+a];
                
                for i in range(0,len(correct_list)-a):
                    if (correct_list[i][j] == correct_list[i+a][j]):
                        #print "Checking Attribute : ",functions['attribute'][j].__name__;
                        count[a][j] = count[a][j] + (1);
                        
                    else:
                        #count[a][j] = count[a][j] - (10);
                        count2[a][j] = count2[a][j] + (1);
                        
                        pass;
                
                if(count[a][j]>max):
                    #print "Matching : ",correct_list[i][j],"  ",correct_list[i+a][j],"   ",count[a][j];
                    max = count[a][j];
                    maxe = count2[a][j];
                    var_2 = a;
                    var_3 = j;
                    #var_4 = i;
                    #print "VAR 4 ",var_4;

                
                    
            #print count;
        for a in range(lenG,0,-1):
            for i in range(0,len(correct_list)-a):
                for j in range(2,len(correct_list[var_4])):
                    if count[var_2][j]==max : 
                        var_1.add(j);


        #print "Maximum Correct Cards : "+str(max);
        print "Periodicity : "+str(var_2);
        #print var_1;
        print functions['attribute'][var_3].__name__;
        #print var_1;
        #for f in range(len(functions['attribute'])):
            #print "Fishy here"
        print "======================="
        print "Common attributes";
        for i1 in var_1:
            print functions['attribute'][i1].__name__;
        #print functions[var_1];

        print "Efficiency "

        total_eff = max + maxe;
        if(total_eff != 0):
            print (float)(max*100/total_eff);
        


        


    def neighborhood(iterable):
        iterator = iter(iterable)
        prev_item = None
        current_item = next(iterator)  # throws StopIteration if empty.
        for next_item in iterator:
            yield (prev_item, current_item, next_item)
            prev_item = current_item
            current_item = next_item
        yield (prev_item, current_item, None)

    def playNext(self, runCount = None):
        print "playNext"
        player = self.nextPlayer()
        play = None
        card = None
        os.system('clear')
        self.printRecord()
        lastPlays = []
        events = []
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
        os.system('clear')
        self.printRecord()
        if self.randomPlay and (runCount is None or self.playRun < runCount):
            self.playRun = self.playRun + 1
            nextPlay = self.playNext(runCount = runCount)
        else:
            self.playRun = 0

        return [(events, correct)] + nextPlay

if __name__ == "__main__":
    game = Game(Card(sys.argv[1][:-1], sys.argv[1][len(sys.argv[1])-1:]), rule=sys.argv[2], randomPlay = True)
    game.playNext(15)