import sys
import pdb
import eleusis
import eleusis_test as GameModule
from eleusis_test import Selector
from eleusis_test import Card
import copy

lang = GameModule.Language()

KB = {
    ("suit", ("C", "S")): Selector("color", Selector.CIRCULAR, Card.domain["color"], '==', "B"),
    ("suit", ("D", "H")): Selector("color", Selector.CIRCULAR, Card.domain["color"], '==', "R"),
    ("color", ("B",)): Selector("suit", Selector.CIRCULAR, Card.domain["suit"], '==', ["C", "S"]),
    ("color", ("R",)): Selector("suit", Selector.CIRCULAR, Card.domain["suit"], '==', ["D", "H"]),
    # ("parity", (0,)): Selector("value", Selector.INTERVAL, Card.domain["value"], '==', [2, 4, 6, 8, 10 ,12]),
    # ("parity", (1,)): Selector("value", Selector.INTERVAL, Card.domain["value"], '==', [1, 3, 5, 7, 9 ,11, 13]),
    # ("value", (2, 4, 6, 8, 10 ,12)): Selector('parity', Selector.NOMINAL, [0, 1], '==', [0]),
    # ("value", (1, 3, 5, 7, 9 ,11, 13)): Selector('parity', Selector.NOMINAL, [0, 1], '==', [1])
}

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
    'lookback': 0
}

def printDesc(event, newLine=True):
    if isinstance(event, Selector):
        print str(event),
    else:
        for desc in event:
            if isinstance(desc, dict) or isinstance(desc, list):
                printDesc(desc)
            elif isinstance(event, dict):
                print str(event[desc]),
            elif isinstance(desc, Selector):
                print str(desc),
    if newLine:
        print ''

## Problem specific, Given two episode descriptions, generate meta attributes between them
def getMetaAttributes(episode1, episode2 = None):
    metaAttributes = {}
    metaAttributes['parity' + str(episode1[1])] =  Selector('parity', Selector.NOMINAL, [0, 1], '==', episode1[0]['value' + str(episode1[1])].getReference() % 2, str(episode1[1]))

    if episode2 is not None:
        metaAttributeList = ['value', 'suit', 'color']

        for i in metaAttributeList:
            metaAttributes['d' + i + str(episode1[1]) + str(episode2[1])] = episode1[0][i + str(episode1[1])].difference(episode2[0][i + str(episode2[1])])

        metaAttributes['parity' + str(episode2[1])] =  Selector('parity', Selector.NOMINAL, [0, 1], '==', episode2[0]['value' + str(episode2[1])].getReference() % 2, str(episode2[1]))


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
        eventDescription.update(getMetaAttributes((outcome, 0)))
        for i in range(0, lookback):
            index = size - lookback
            lookbackDesc = getEventEpisodeDescription(event[0][index], i + 1)
            lookbackDesc.update(getMetaAttributes((outcome, 0), (lookbackDesc, i+1)))
            eventDescription.update(lookbackDesc)

        if event[1]:
            pos.append(eventDescription)
        else:
            neg.append(eventDescription)
    return pos, neg


def getComplimentaryReference(type, originalCover, removeCover=[], addCover=[]):
    if not isinstance(originalCover, list):
        originalCover = [originalCover]
    if not isinstance(removeCover, list):
        removeCover = [removeCover]
    if not isinstance(addCover, list):
        addCover = [addCover]

    newCover = []

    if isinstance(removeCover, tuple):
        removeCover = range(removeCover[0], removeCover[1] + 1)
    elif not isinstance(removeCover, list):
        removeCover = [removeCover]

    if isinstance(addCover, tuple):
        addCover = range(addCover[0], addCover[1] + 1)
    elif not isinstance(addCover, list):
        addCover = [addCover]

    for i in originalCover:
        if isinstance(i, tuple):
            newCover = newCover + [j for j in range(i[0], i[1]+1) if j not in removeCover]
        elif i not in removeCover:
            newCover.append(i)

    newCover = list(set(newCover) | set(addCover))
    newCover.sort()

    if type == Selector.INTERVAL and len(newCover) > 0:
        originalCover = newCover
        newCover = []
        index = 0
        counter = 0
        for i in range(1, len(originalCover)):

            if originalCover[i] - originalCover[i-1] == 1:
                counter = counter + 1

            if originalCover[i] - originalCover[i-1] > 1:
                if counter < 2:
                    newCover = newCover + originalCover[index: index+counter + 1]
                else:
                    newCover.append((originalCover[index], originalCover[index+counter]))
                index = i
                counter = 0
        if counter < 2:
            newCover = newCover + originalCover[index: index+counter + 1]
        else:
            newCover.append((originalCover[index], originalCover[index+counter]))

    return newCover

def conjunct(cp1, cp2, compare=False):
    conjunction = {}

    cp12 = set(cp1.keys()).intersection(set(cp2.keys()))
    cp1n2 = set(cp1.keys()).difference(set(cp2.keys()))
    cp2n1 = set(cp2.keys()).difference(set(cp1.keys()))

    for i in cp12:
        selector = copy.deepcopy(cp1[i])
        eRef1, eRef2 = cp1[i], cp2[i]
        if isinstance(cp1[i], Selector):
            eRef1 = cp1[i].getExpandedReference()
        if isinstance(cp2[i], Selector):
            eRef2 = cp2[i].getExpandedReference()

        try:
            eRef1, eRef2 = set(eRef1), set(eRef2)
        except:
            pdb.set_trace()

        if (compare and eRef1 != eRef2):
            return None

        newRef = list(eRef1.intersection(eRef2))

        if len(newRef) == 0:
            return None

        selector.setReference(newRef)
        conjunction[i] = selector

    for i in cp1n2:
        conjunction[i] = cp1[i]

    for i in cp2n1:
        conjunction[i] = cp2[i]

    return conjunction

def filterAndExtendFromKB(cpx):
    ruleSet = {}
    for sel in cpx:
        cid = cpx[sel].getIdentifier()
        ruleSet = conjunct(ruleSet, {sel: cpx[sel]}, True)
        if ruleSet is None:
            return None
        for kb in KB:
            if kb[0] == cid and cpx[sel].test(list(kb[1]), True):
                kbImplication = copy.deepcopy(KB[kb])
                kbImplication.setSPID(cpx[sel].getSPID())
                ruleSet = conjunct(ruleSet, {(KB[kb].getIdentifier() + cpx[sel].getSPID()) : kbImplication}, True)
                if ruleSet is None:
                    return None

    return ruleSet

def Star(seed, negatives):
    ruleCover = []

    for neg in negatives:

        cover = []
        CDF = {}

        for sel in neg:
            selector = copy.deepcopy(neg[sel])
            selector.setReference(getComplimentaryReference(selector.getType(), selector.getDomain(), removeCover=selector.getReference()))
            if len(ruleCover) == 0:
                cover.append({sel: selector})
            else:
                for rule in ruleCover:
                    if selector.test(seed[selector.getName()]):
                        conjunction = conjunct(rule, {sel: selector})
                        if conjunction is not None and conjunction not in cover:
                            conjunction = filterAndExtendFromKB(conjunction)
                            if conjunction is not None:
                                cover.append(conjunction)

        ruleCover = cover

    cover = ruleCover
    ruleCover = []

    for rule in cover:
        negSatisfied = False

        for neg in negatives:
            singleSatisfy = True
            for sel in neg:
                if sel in rule and not rule[neg[sel].getName()].test(neg[sel]):
                    singleSatisfy = False
                    break
            if singleSatisfy:
                negSatisfied = True
                break

        if not negSatisfied:
            ruleCover.append(rule)
    printDesc(ruleCover)
    return ruleCover

proposedRule = []

def satisfyEvent(cpx, event):
    for sel in cpx:
        if not cpx[sel].test(event[sel]):
            return False
    return True

def isCoveredByProposed(event):
    for cpx in proposedRule:
        if satisfyEvent(cpx, event):
            return True
    return False

def LEF(cover, pos, neg, MAXSTAR=4):
    newCover = []
    rank = []
    perfectCover = {}
    for rule in cover:
        pCount = 0
        nCount = 0
        for event in pos:
            if satisfyEvent(rule, event):
                pCount = pCount + 1

        for event in neg:
            if satisfyEvent(rule, event):
                nCount = nCount + 1

        domainCover = 1.0
        for sel in rule:
            domainCover = domainCover * float(len(rule[sel].getExpandedReference()))/float(len(rule[sel].getExpandedDomain()))

        if domainCover > 1:
            pdb.set_trace()

        pRatio = float(pCount)/len(pos)
        nRatio = float(nCount)/len(neg)

        if nRatio >= 0.25 or pRatio <= 0.25:
            print "skipping",
            printDesc(rule)
            continue

        if pRatio == 1:
            perfectCover = conjunct(perfectCover, rule)
            print "perfect",

        rank.append((pRatio - nRatio, rule))


        print str(rank[-1][0]) + ", " + str(domainCover) + " :",
        printDesc(rule)

    if len(perfectCover) > 0:
        rank.append((1,perfectCover))

    rank.sort(reverse=True)

    print '\n\n'
    for rule in rank:
        print rule[0],
        printDesc(rule[1])

    pdb.set_trace()
    # for i in range(0, len(cover)):
    #     if rank[i][1] == 1:
    #         perfectCover = conjunct(perfectCover, cover[i])
    #     else if rank[i][0] >= 0.5 and rank[i][1] <= 0.25:
    #         newCover.append(cover[i])


## Generate a cover of all positives, so that no negative is covered
def AQ(pos, neg):
    covers = []

    print 'Neg: '
    printDesc(neg)
    print str(len(pos)) + ", " + str(len(neg)) + "; Covers : "
    for seed in pos:
        pdb.set_trace()
        if isCoveredByProposed(seed):
            continue
        cover = Star(seed, neg)
        LEF(cover, pos, neg)
        # rankCovers(cover)
        proposedRule.extend(cover)
        print ''
        printDesc(cover)

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
        pdb.set_trace()
        printDesc(pos)
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


















