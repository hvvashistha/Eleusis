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
#   https://docs.python.org/2/library/datetime.html


print "Inside Rule_Estimation.py";

import sys
import pdb
import eleusis
import eleusis_test as GameModule
from eleusis_test import Selector

lang = GameModule.Language()

def notF(inputV):
    return not inputV

def evenF(inputV):
    return inputV % 2 == 0

def distanceF(inputV1, inputV2, domain):
    l = None
    if isinstance(domain, set):
        return inputV2 - inputV1
    else:
        return domain.index(inputV2) - domain.index(inputV1)


operators = {
    'notO': GameModule.Operator(notF, 1),
    'evenO': GameModule.Operator(evenF, 1),
    'greaterO': GameModule.Operator(eleusis.to_function['greater'], 2),
    'lessO': GameModule.Operator(eleusis.to_function['less'], 2),
    'equalO': GameModule.Operator(eleusis.to_function['equal'], 2),
    'distanceO': GameModule.Operator(distanceF, 3)
}

params = {
    'lookback': 1
}

def printDesc(event):
    print "Print Description"
    for desc in event:
        print str(desc if isinstance(event, list) else event[desc]),
    print ''

## Problem specific, Given two episode descriptions, generate meta attributes between them
def getMetaAttributes(episode1, episode2):
    #dvalue, dsuit, dcolor
    metaAttributeList = ['value', 'suit', 'color']

    metaAttributes = {}

    for i in metaAttributeList:
        metaAttributes['d' + i + str(episode1[1]) + str(episode2[1])] = episode1[0][i + str(episode1[1])].difference(episode2[0][i + str(episode2[1])])
    return metaAttributes

## Problem specific, breaks down Entities like Card into their attributes
def getEventEpisodeDescription(eventEpisode, lookback = None):
    description = {}
    for sel in eventEpisode:
        sel.setSPID(lookback)
        description[sel.getName()] = sel

    return description


##########################
# Learning system

# Generates a full description of events in each sequence, adding meta attributes and separating them into positive and negative sets
def describe(events, lookback):
    pos = []
    neg = []
    for event in events:
        eventDescription = {}
        size = len(event[0]) - 1
        outcome = getEventEpisodeDescription(event[0][size], 0)
        eventDescription.update(outcome)
        for i in range(0, lookback):
            index = size - lookback
            lookbackDesc = getEventEpisodeDescription(event[0][index], i + 1)
            lookbackDesc.update(getMetaAttributes((outcome, 0), (lookbackDesc, i+1)))
            eventDescription.update(lookbackDesc)

        # printDesc(eventDescription)

        if event[1]:
            pos.append(eventDescription)
        else:
            neg.append(eventDescription)
    return pos, neg

#remove from reference
def getComplimentaryReference(type, originalcover, removeCover=[], addCover=[]):
    newCover = []

    if isinstance(removeCover, tuple):
        removeCover = range(removeCover[0], removeCover[1] + 1)
    elif not isinstance(removeCover, list):
        removeCover = [removeCover]

    if isinstance(addCover, tuple):
        addCover = range(addCover[0], addCover[1] + 1)
    elif not isinstance(addCover, list):
        addCover = [addCover]

    for i in originalcover:
        if isinstance(i, tuple):
            newCover = newCover + [j for j in range(i[0], i[1]+1) if j not in removeCover]
        elif i not in removeCover:
            newCover.append(i)

    newCover = list(set(newCover) | set(addCover))
    newCover.sort()

    if type == Selector.INTERVAL:
        originalcover = newCover
        newCover = []
        index = 0
        counter = 0
        for i in range(1, len(originalcover)):

            if originalcover[i] - originalcover[i-1] == 1:
                counter = counter + 1

            if originalcover[i] - originalcover[i-1] > 1:
                if counter < 2:
                    newCover = newCover + originalcover[index: index+counter + 1]
                else:
                    newCover.append((originalcover[index], originalcover[index+counter]))
                index = i
                counter = 0
        if counter < 2:
            newCover = newCover + originalcover[index: index+counter + 1]
        else:
            newCover.append((originalcover[index], originalcover[index+counter]))

    return newCover if len(newCover) > 1 else newCover[0]

def Star(seed, negatives):
    r = []
    # print "seed: ",
    # printDesc(seed)

    star = []  #Covers everything
    ruleCover = []  #Useless, when star above is implemented

    for neg in negatives:
        # print "negative: ",
        # printDesc(neg)
        ruleComplex = []
        # Generate complementary complex for negative event
        for sel in neg:
            selector = neg[sel]

            if seed[selector.getName()] != selector:
                #Above condition is equivalent to LEF trimming on maxstar, #Compliment of negative event covers seed only when neg != pos

                #Getting compliment of negative, covers positive
                selector.setReferece(getComplimentaryReference(selector.getType(), selector.getDomain(), removeCover=selector.getReference()))

                # if selector.test(seed[selector.getName()]):
                # intersection = star[selector.getName()].intersect(selector)
                # if intersection.test(seed[intersection.getName()]):
                #     star[intersection.getName()] = intersection

                ruleComplex.append(selector)    #useless, directly intersect

        ruleCover.append(ruleComplex)

    print "cover: "
    for i in ruleCover:
        printDesc(i)

## Generate a cover of all positives, so that no negative is covered
def AQ(pos, neg):
    for seed in pos:
        ruleSet = Star(seed, neg)
        pdb.set_trace()

##################

def emulate_Play(numberOfPlayers = 6):
    
    rule = sys.argv[2]
    numberOfPlays = 1
    game = GameModule.Game(GameModule.Card(sys.argv[1][:-1], sys.argv[1][len(sys.argv[1])-1:]), rule=sys.argv[2], randomPlay = True, players=numberOfPlayers)
    #God played

    historicalSequences = []

    eventSets = {
        'positive': [],
        'negative': []
    }

    #Time for players to play
    for i in range(0, numberOfPlays):
        pos, neg = describe(game.playNext(runCount = numberOfPlayers), params['lookback'])
        eventSets['positive'] = eventSets['positive'] + pos
        eventSets['negative'] = eventSets['negative'] + neg
        if len(pos) == 0 or len(neg) == 0:
            continue
        else:   #Start learning here

            # Decomposition model fitting
            # decompose(eventSets['positive'], eventSets['negative'])

            # Periodic model fitting, if required
            #

            #DNF Model fitting, Very large search space, execute only if necessary
            AQ(eventSets['positive'], eventSets['negative'])


                #Learning code ends
            #Reset event set, for new learning episode
            historicalSequences.append(eventSets)
            eventSets['positive'] = []
            eventSets['negative'] = []

if __name__ == "__main__":
    emulate_Play()