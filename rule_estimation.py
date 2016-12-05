import sys
import pdb
import eleusis
import eleusis_test as GameModule
from eleusis_test import Selector
from eleusis_test import Card
import copy
import time

lang = GameModule.Language()

KB = {
    ("suit", ("C", "S")): Selector("color", Selector.NOMINAL, Card.domain["color"], '==', set(["B"])),
    ("suit", ("D", "H")): Selector("color", Selector.NOMINAL, Card.domain["color"], '==', set(["R"])),
    ("suit", ("C")): Selector("color", Selector.NOMINAL, Card.domain["color"], '==', set(["B"])),
    ("suit", ("B")): Selector("color", Selector.NOMINAL, Card.domain["color"], '==', set(["B"])),
    ("suit", ("D")): Selector("color", Selector.NOMINAL, Card.domain["color"], '==', set(["R"])),
    ("suit", ("H")): Selector("color", Selector.NOMINAL, Card.domain["color"], '==', set(["R"])),
    ("color", ("B",)): Selector("suit", Selector.CIRCULAR, Card.domain["suit"], '==', set(["C", "S"])),
    ("color", ("R",)): Selector("suit", Selector.CIRCULAR, Card.domain["suit"], '==', set(["D", "H"])),
    ("parity", (0,)): Selector("value", Selector.INTERVAL, Card.domain["value"], '==', set([2, 4, 6, 8, 10 ,12])),
    ("parity", (1,)): Selector("value", Selector.INTERVAL, Card.domain["value"], '==', set([1, 3, 5, 7, 9 ,11, 13])),
    ("value", (2, 4, 6, 8, 10 ,12)): Selector('parity', Selector.NOMINAL, set([0, 1]), '==', set([0])),
    ("value", (1, 3, 5, 7, 9 ,11, 13)): Selector('parity', Selector.NOMINAL, set([0, 1]), '==', set([1]))
}

hammingVector = {
    "suit": 1,
    "value": 0.6,
    "parity": 1,
    "color": 0.9,
    "dvalue": 0.8,
    "dsuit": 1
}

threshold = {
    "positives": 0.25,
    "negatives": -0.25,
    "sameRuleDistance": 0.2,
    "domainCover": -0.6,
    "MAXSTAR": 6
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

def printRank(ranks):
    for i in ranks:
        print str(i[0]) + " :",
        printDesc(i[1])

def printDesc(event, prefix=None, newLine=True):
    if prefix is not None:
        print prefix,
        if newLine:
            print ''
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

    metaAttributes['parity' + str(episode1[1])] =  Selector('parity', Selector.NOMINAL, set([0, 1]), '==', set([episode1[0]['value' + str(episode1[1])].get() % 2]), str(episode1[1]))

    if episode2 is not None:
        metaAttributeList = ['value', 'suit', 'color']

        for i in metaAttributeList:
            metaAttributes['d' + i + str(episode1[1]) + str(episode2[1])] = episode1[0][i + str(episode1[1])].difference(episode2[0][i + str(episode2[1])])

        metaAttributes['parity' + str(episode2[1])] =  Selector('parity', Selector.NOMINAL, set([0, 1]), '==', set([episode2[0]['value' + str(episode2[1])].get() % 2]), str(episode2[1]))
    return metaAttributes

## Problem specific, breaks down Entities like Card into their attributes
def getEventEpisodeDescription(eventEpisode, lookback = None):
    eventComplex = {}
    for sel in eventEpisode:
        sel.setSPID(lookback)
        eventComplex[sel.getName()] = sel

    return eventComplex


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

def multiply(cp1, cp2, referenceConjuctionCheck=False):
    if isinstance(cp1, list) and isinstance(cp2, list):     #Conjunction of OR
        conjunction = []
        for cpx1 in cp1:
            for cpx2 in cp2:
                conjunctedCpx = multiply(cpx1, cpx2)
                if conjunctedCpx is not None and conjunctedCpx not in conjunction:
                    conjunction.append(conjunctedCpx)

        if len(cp1) > 0 and len(cp2) > 0:
            return conjunction
        else:
            return cp1 or cp2

    elif isinstance(cp1, dict) and isinstance(cp2, dict):   #Conjunction of AND
        conjunction = {}
        refConjuncted = False

        cp12 = set(cp1.keys()) & set(cp2.keys())
        cp1n2 = set(cp1.keys()) - set(cp2.keys())
        cp2n1 = set(cp2.keys()) - set(cp1.keys())

        for i in cp12:
            refConjuncted = cp1[i] != cp2[i]
            newRef = cp1[i] & cp2[i]
            if len(newRef) == 0:                            # cp1[i] & cp2[i] = {} = False complex
                return (None, None) if referenceConjuctionCheck else None
            conjunction[i] = newRef

        for i in cp1n2:
            conjunction[i] = cp1[i]

        for i in cp2n1:
            conjunction[i] = cp2[i]

        return (conjunction, refConjuncted) if referenceConjuctionCheck else conjunction

    else:
        raise TypeError("Type of two complexes should be same. dict() for ANDed complexes, list() for ORed complexes")

def filterAndExtendFromKB(cpx):
    disjuncts = {}
    ruleSet = {}

    for sel in cpx:
        cid = cpx[sel].getIdentifier()

        cover1 = ruleSet[sel] if sel in ruleSet else None
        cover2 = cpx[sel]

        ruleSet, conjuncted = multiply(ruleSet, {sel: cpx[sel]}, True)

        if ruleSet is None:
            break

        if conjuncted and cover1 is not None:
            s1 = cover1 & cover2
            s2 = cover2 - s1.getReference()
            if len(s1) > 0 and len(s2) > 0:
                del ruleSet[sel]
                disjuncts[sel] = [s1, s2]

        for kb in KB:
            if kb[0] == cid and cpx[sel].test(set(kb[1]), True):
                kbImplication = KB[kb].copy()
                kbImplication.setSPID(cpx[sel].getSPID())
                cover2 = kbImplication

                ruleSet, conjuncted = multiply(ruleSet, {(KB[kb].getIdentifier() + cpx[sel].getSPID()) : kbImplication}, True)

                if ruleSet is None:
                    break

                if conjuncted and cover1 is not None:
                    s1 = cover1 & cover2
                    s2 = cover1 - s1.getReference()
                    if len(s1) > 0 and len(s2) > 0:
                        del ruleSet[sel]
                        disjuncts[sel] = [s1, s2]

    rule = []
    if ruleSet is not None:
        rule = [ruleSet]
        for name in disjuncts:
            intermediateRule = []
            for sel in disjuncts[name]:
                for ruleComplex in rule:
                    intermediateRule.extend(filterAndExtendFromKB(multiply(ruleComplex, {name: sel})))
            rule = intermediateRule

    return rule

def Star(seed, negatives, ruleCover = []):
    oT = time.time()
    for neg in negatives:
        cover = []
        CDF = {}
        for sel in neg:
            if sel in seed and not neg[sel].test(seed[sel]):
                cSelector = None
                if seed[sel].getSPID() == '0' or seed[sel].getType() == Selector.NOMINAL:
                    cSelector = neg[sel].getCompliment()
                else:
                    if seed[sel].getType() == Selector.INTERVAL or seed[sel].getType() == Selector.CIRCULAR:
                        cSelector = seed[sel].copy()
                        i1 = cSelector.getSortedDomain().index(cSelector.get())
                        i2 = neg[sel].getSortedDomain().index(neg[sel].get())
                        ref = set(cSelector.getSortedDomain()[0:i2]) if i1 < i2 else set(cSelector.getSortedDomain()[i2+1:])
                        cSelector.setReference(ref)

                extended = filterAndExtendFromKB({sel: cSelector})
                if extended is not None and extended not in cover:
                    cover.extend(extended)

        ruleCover = [] or multiply(ruleCover, cover)
    iT = time.time()
    print "star complete, cover length : " + str(len(ruleCover))
    print "Time taken by star(" + str(len(negatives)) + "," + str(len(ruleCover)) + "): " + str(iT - oT)
    return ruleCover

ranks = []
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

def generalizeSimilarRules(cover):
    newCover = []
    covered = set()
    ruleMergeList = []

    for i in range(0, len(cover)):
        if i in covered:
            continue
        rule = cover[i]
        similars = set([i])
        for j in range(i + 1, len(cover)):
            if j in covered:
                continue
            cRule = cover[j]
            dist = 0
            keys = set(rule.keys()).union(set(cRule.keys()))

            for sel in keys:
                SIR = sel in rule
                SIC = sel in cRule
                identifier = rule[sel].getIdentifier() if SIR else cRule[sel].getIdentifier()
                domain = rule[sel].getDomain() if SIR else cRule[sel].getDomain()

                union, intersection = None, None

                if not SIR:
                    intersection = len(cRule[sel].getReference() if SIC else domain)
                    union = len(domain)
                elif not SIC:
                    intersection = len(rule[sel].getReference() if SIR else domain)
                    union = len(domain)
                else:
                    intersection = len(rule[sel].getReference() & cRule[sel].getReference())
                    union = len(rule[sel].getReference() | cRule[sel].getReference())

                selDist = 1.0 - float(intersection)/float(union)
                dist += (selDist * hammingVector[identifier]) if identifier in hammingVector else selDist

            if (dist <= threshold["sameRuleDistance"]):
                similars |= set([j])
                covered |= set([j])

        ruleMergeList.append(similars)

    for rSet in ruleMergeList:
        similars = list(rSet)
        merged = cover[similars[0]]

        for i in range(1, len(similars)):
            nRule = cover[similars[i]]

            for sel in nRule:
                if sel in merged:
                    merged[sel] |= nRule[sel]

        merged = filterAndExtendFromKB(merged)
        for rule in merged:
            for sel in rule.keys():
                if float(len(rule[sel]))/len(rule[sel].getDomain()) > 0.8:
                    del rule[sel]

            if len(rule) > 0 and rule not in newCover:
                newCover.append(rule)

    return newCover

def addRankVectors(rules, pos, neg, testingPhase=False, lastEventSet=None):
    rank = []
    for rankedCpx in rules:
        rule = rankedCpx
        if testingPhase:
            assert lastEventSet is not None
            rule = rankedCpx[1]

        pCount = 0
        nCount = 0
        pCover = []
        nCover = []
        for event in pos:
            if satisfyEvent(rule, event):
                pCount = pCount + 1
                pCover.append(event)

        for event in neg:
            if satisfyEvent(rule, event):
                nCount = nCount + 1
                nCover.append(event)

        domainCover = 1
        pRatio = 0
        nRatio = 0
        pLen = len(pos)
        nLen = len(neg)

        if not testingPhase:
            suits = len(rule['suit0']) if 'suit0' in rule else 4
            values = len(rule['value0']) if 'value0' in rule else 13
            domainCover = round(float(suits * values)/52.0,3)
            pRatio = round(float(pCount)/pLen,3)
            nRatio = round(float(nCount)/nLen,3)
        else:
            nCount = nCount - (rankedCpx[0][1] * lastEventSet[1])
            nLen = nLen + lastEventSet[1]
            nRatio = round(float(nCount)/nLen,3)
            cpCount = pCount + rankedCpx[0][2]
            pLen = pLen + lastEventSet[0]
            pRatio = round(float(cpCount)/pLen,3)
            if nRatio == 0:                                 #If negative cover is 0.0, Do not let rule rank be affected by play bias
                pRatio = rankedCpx[0][0]
                pCount = cpCount

            domainCover = -rankedCpx[0][3]

        rank.append(((pRatio, -nRatio, pCount, -domainCover), rule, (pCover, nCover)))

    rank.sort(key=lambda x: x[0], reverse=True)

    return rank

def LEF(cover, pos, neg, MAXSTAR=6, incrementing=False):
    print "LEF start"
    oT = time.time()
    cover = generalizeSimilarRules(cover)
    iT = time.time()
    print "Time taken by generalizeSimilarRules(" + str(len(cover)) + "): " + str(iT - oT)
    oT = iT
    rank = addRankVectors(cover, pos, neg)
    iT = time.time()
    print "Time taken by addRankVectors(" + str(len(cover)) + "," + str(len(pos)) + "," + str(len(neg)) + "): " + str(iT - oT)

    if len(rank) > 0:
        rank = rank[:min(len(rank), MAXSTAR)]
        fRank = filter(
            lambda x: x[0][0] >= (0.6 if incrementing else threshold["positives"]) and x[0][1] >= threshold["negatives"] and x[0][3] >= threshold["domainCover"],
            rank)

        if len(fRank) == 0 and not incrementing:
            rank = [rank[0]]
        else:
            rank = fRank
    print "LEF end"
    return rank

def incrementalUpdate(rank, pos, neg, lastEventSet):
    print "Incremental Learning Start\n"
    rank = addRankVectors(rank, pos, neg, True, lastEventSet)

    newCover = []
    newRanks = []
    for rankedCpx in rank:
        if rankedCpx[0][1] != 0:
            for seed in rankedCpx[2][0]:
                nCover = Star(seed, rankedCpx[2][1], [rankedCpx[1]])
                seedRank = LEF(nCover, pos, neg, MAXSTAR = threshold["MAXSTAR"], incrementing = True)
                for i in seedRank:
                    if i[1] not in newCover:
                        newRanks.append((i[0], i[1]))
                        newCover.append(i[1])
        elif rankedCpx[1] not in newCover:
            newRanks.append((rankedCpx[0], rankedCpx[1]))
            newCover.append(rankedCpx[1])

    ranks[:] = newRanks
    proposedRule[:] = newCover
    print "Incremental Learning Complete\n"

def findAndMergeExactSubsets(ranks):
    merge = []
    lastMerged = None
    for i in range(1, len(ranks)):
        lastRank = lastMerged[0] if lastMerged is not None else ranks[i-1]

        lRank = lastRank if lastRank[0][3] < ranks[i][0][3] else ranks[i]
        rRank = ranks[i] if lastRank[0][3] < ranks[i][0][3] else lastRank

        subSet = True

        if lRank[0][0] >= rRank[0][0] and lRank[0][1] >= rRank[0][1] and lRank[0][3] > threshold["domainCover"]:
            keys = set(lRank[1].keys()).union(rRank[1].keys())
            for sel in keys:
                s1, s2 = None, None
                domain = None
                SIL = sel in lRank[1]

                identifier = lRank[1][sel].getIdentifier() if SIL else rRank[1][sel].getIdentifier()

                if identifier == "suit" or identifier == "value":
                    domain = lRank[1][sel].getDomain() if SIL else rRank[1][sel].getDomain()
                    s1 = lRank[1][sel] if SIL else domain
                else:
                    continue

                s2 = rRank[1][sel] if sel in rRank[1] else domain
                if not (s1 >= s2):         #If s2 is not a subset of s1
                    subSet = False
                    break
        else:
            subSet = False

        if subSet:
            if lastMerged is None or lRank not in lastMerged:
                merge.append(lRank)
            lastMerged = (lRank, rRank)
        else:
            if lastMerged is None:
                merge.append(ranks[i-1])
            lastMerged = None

    if lastMerged is None:
        merge.append(ranks[-1])

    return merge

## Generate a cover of all positives, so that no negative is covered
def AQ(pos, neg, lastEventSet):
    negatives = []

    while neg:
        negatives.append(neg[0:5])
        neg = neg[5:]

    while negatives:
        neg = negatives.pop()
        covers = []

        print "\nAQ new event set iteration\n"
        if len(ranks) > 0:
            incrementalUpdate(ranks, pos, neg, lastEventSet)

        for seed in pos:
            if isCoveredByProposed(seed):
                continue

            cover = Star(seed, neg)

            seedRank = LEF(cover, pos, neg, MAXSTAR = threshold["MAXSTAR"], incrementing = False)

            for i in seedRank:
                ranks.append((i[0], i[1]))
                proposedRule.append(i[1])

        ranks.sort(key=lambda x: x[0], reverse=True)

        print "\nAQ iteration complete\n"

        while True:
            newRanks = findAndMergeExactSubsets(ranks)
            if ranks != newRanks:
                ranks[:] = newRanks
            else:
                break

        proposedRule[:] = map(lambda x: x[1], ranks)

    return proposedRule
##################

def emulate_Play(numberOfPlayers = 8):
    rule = sys.argv[2]
    numberOfPlays = 20
    game = GameModule.Game(GameModule.Card(sys.argv[1][:-1], sys.argv[1][len(sys.argv[1])-1:]), rule=sys.argv[2], randomPlay = True, players=numberOfPlayers)
    #God played

    historicalSequences = []

    eventSets = {
        'positive': [],
        'negative': []
    }
    lastEventSet = (0, 0)
    #Time for players to play
    for i in range(0, numberOfPlays):
        pos, neg = describe(game.playNext(runCount = numberOfPlayers), params['lookback'])

        eventSets['positive'] = eventSets['positive'] + pos
        eventSets['negative'] = eventSets['negative'] + neg

        if len(pos) == 0 or len(neg) == 0:
            continue
        else:
            print "\n\nNew round of cards:\n"
            game.printRecord(numberOfPlayers + 1)
            #Start learning here

            # Decomposition model fitting
            # decompose(eventSets['positive'], eventSets['negative'])

            # Periodic model fitting, if required
            #

            #DNF Model fitting, Very large search space, execute only if necessary
            printDesc(AQ(eventSets['positive'], eventSets['negative'], lastEventSet))
            lastEventSet = (len(pos), len(neg))

            #Learning code ends
            #Reset event set, for new learning episode
            historicalSequences.append(eventSets)
            eventSets['positive'] = []
            eventSets['negative'] = []

if __name__ == "__main__":
    emulate_Play()

