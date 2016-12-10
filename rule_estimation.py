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
    ("suit", frozenset(["C", "S"])): Selector("color", Selector.NOMINAL, Card.domain["color"], '==', set(["B"])),
    ("suit", frozenset(["D", "H"])): Selector("color", Selector.NOMINAL, Card.domain["color"], '==', set(["R"])),
    ("suit", frozenset(["C"])): Selector("color", Selector.NOMINAL, Card.domain["color"], '==', set(["B"])),
    ("suit", frozenset(["B"])): Selector("color", Selector.NOMINAL, Card.domain["color"], '==', set(["B"])),
    ("suit", frozenset(["D"])): Selector("color", Selector.NOMINAL, Card.domain["color"], '==', set(["R"])),
    ("suit", frozenset(["H"])): Selector("color", Selector.NOMINAL, Card.domain["color"], '==', set(["R"])),
    ("color", frozenset(["B"])): Selector("suit", Selector.CIRCULAR, Card.domain["suit"], '==', set(["C", "S"])),
    ("color", frozenset(["R"])): Selector("suit", Selector.CIRCULAR, Card.domain["suit"], '==', set(["D", "H"])),
    ("parity", frozenset([0])): Selector("value", Selector.INTERVAL, Card.domain["value"], '==', set([2, 4, 6, 8, 10 ,12])),
    ("parity", frozenset([1])): Selector("value", Selector.INTERVAL, Card.domain["value"], '==', set([1, 3, 5, 7, 9 ,11, 13])),
    ("value", frozenset([2, 4, 6, 8, 10 ,12])): Selector('parity', Selector.NOMINAL, set([0, 1]), '==', set([0])),
    ("value", frozenset([1, 3, 5, 7, 9 ,11, 13])): Selector('parity', Selector.NOMINAL, set([0, 1]), '==', set([1]))
}

hammingVector = {
    "suit0": 0.6,
    "value0": 0.4,
    "parity0": 1,
    "color0": 1,
    "dvalue01": 0.4,
    "dsuit01": 0.5,
    "suit1": 1,
    "value1": 0.2,
    "parity1": 1,
    "color1": 1,
    "dvalue02": 0.4,
    "dsuit02": 0.5,
    "suit2": 1,
    "value2": 0.2,
    "parity2": 1,
    "color2": 1,
}

threshold = {
    "positives": 0.3,
    "negatives": -0.25,
    "sameRuleDistance": 0.3,
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
            diffRule = episode2[0][i + str(episode2[1])].difference(episode1[0][i + str(episode1[1])])
            if diffRule.get() != 0:
                metaAttributes[diffRule.getName()] = diffRule
                identifier = diffRule.getIdentifier()
                if identifier != 'd_color':
                    orderRule = Selector(identifier + "_order", Selector.NOMINAL, set([-1, 1]), '==',
                        set([1 if diffRule.get() > 0 else -1]), spID = diffRule.getSPID())
                    metaAttributes[orderRule.getName()] = orderRule

        metaAttributes['parity' + str(episode1[1])] =  Selector('parity', Selector.NOMINAL, set([0, 1]), '==', set([episode1[0]['value' + str(episode1[1])].get() % 2]), str(episode1[1]))
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
            lookbackDesc.update(getMetaAttributes((lookbackDesc, i+1), (outcome, 0)))
            eventDescription.update(lookbackDesc)

        if event[1]:
            pos.append(eventDescription)
        else:
            neg.append(eventDescription)

    return pos, neg

def multiply(cp1, cp2, referenceConjuctionCheck=False, lengthCheck = True):
    if isinstance(cp1, list) and isinstance(cp2, list):     #conjunction of OR
        print "multiplication start (" + str(len(cp1)) + ", " + str(len(cp2)) + ")"
        oT = time.time()
        conjunction = []
        for cpx1 in cp1:
            for cpx2 in cp2:
                conjunctedCpx = multiply(cpx1, cpx2)
                if conjunctedCpx is not None and conjunctedCpx not in conjunction:
                    conjunction.append(conjunctedCpx)

        iT = time.time()
        print "multiplication complete, Time taken: " + str(iT - oT)
        if len(cp1) > 0 and len(cp2) > 0:
            return conjunction
        else:
            return cp1 or cp2

    elif isinstance(cp1, dict) and isinstance(cp2, dict):   #conjunction of AND
        conjunction = {}
        refConjuncted = False
        cp1k = set(cp1.keys())
        cp2k = set(cp2.keys())
        cp12 = cp1k & cp2k
        cp1n2 = cp1k - cp12
        cp2n1 = cp2k - cp12
        lcp12 = len(cp12)

        if lengthCheck and lcp12 + len(cp1k) + len(cp2k) - (2 * lcp12) > 4:
            return (None, None) if referenceConjuctionCheck else None

        for i in cp12:
            refConjuncted = cp1[i] != cp2[i]
            newRef = cp1[i] & cp2[i]
            if len(newRef) == 0:                            # cp1[i] & cp2[i] = {} = False complex
                return (None, None) if referenceConjuctionCheck else None
            conjunction[i] = newRef

        for i in cp1n2:
            if len(cp1[i]) == 0:
                return (None, None) if referenceConjuctionCheck else None
            conjunction[i] = cp1[i]

        for i in cp2n1:
            if len(cp2[i]) == 0:
                return (None, None) if referenceConjuctionCheck else None
            conjunction[i] = cp2[i]

        for sel in conjunction:
            if len(conjunction[sel].getReference()) == 0:
                printDesc(conjunction, "conjunction > ")
                pdb.set_trace()

        conjunction = distanceKB(resolveFromKB(conjunction))

        return (conjunction, refConjuncted) if referenceConjuctionCheck else conjunction

    else:
        raise TypeError("Type of two complexes should be same. dict() for ANDed complexes, list() for ORed complexes")


def distanceKB(rule, filterOnly = True):
    # return rule
    if rule is None:
        return None

    newCover = []

    diffRuleKeys = (sel for sel in rule if sel[:2] == 'd_')
    cpx = copy.deepcopy(rule)
    cpxConsistent = True

    for sel in diffRuleKeys:
        identifier = cpx[sel].getIdentifier()[2:]
        spid = (cpx[sel].getSPID()[0], cpx[sel].getSPID()[1])

        dRule = cpx[sel]                                        #difference rule
        pRule = identifier + cpx[sel].getSPID()[1]              #previous rule
        cRule = identifier + cpx[sel].getSPID()[0]              #current rule

        newRule = None
        if pRule in cpx and len(cpx[pRule]) == 1:
            pRule = cpx[pRule]

            if pRule.getType() == Selector.NOMINAL:
                newRule = pRule.copy() if dRule.get() == 0 else pRule.getCompliment()
            else:
                newRule = pRule.copy()
                newRule.setReference(set())
                newRule.setSPID(cpx[sel].getSPID()[0])

                for amt in list(dRule.getReference()):
                    try:
                        newRule |= set([pRule.offset(amt)])
                    except:
                        dRule -= set([amt])

        if newRule is not None:
            if cRule in cpx:
                cpx[cRule] &= newRule
            elif not filterOnly:
                cpx[cRule] = newRule

            cRule = cpx[cRule]

        if len(dRule) == 0 or len(cRule) == 0:
            cpxConsistent = False
            break

    if cpxConsistent:
        return cpx
    else:
        return None

def resolveFromKB(cpx):
    if cpx is None:
        return None

    for sel in cpx:
        cid = cpx[sel].getIdentifier()
        for kb in KB:
            if kb[0] == cid and cpx[sel].test(kb[1], True):
                implicatedSel = (KB[kb].getName() + cpx[sel].getSPID())
                if implicatedSel in cpx:
                    cpx[implicatedSel] &= KB[kb]
                    if len(cpx[implicatedSel]) == 0:
                        return None
    return cpx

def extendFromKB(cpx):
    if cpx is None:
        return None

    extended = cpx.copy()
    for sel in cpx:
        cid = cpx[sel].getIdentifier()

        for kb in KB:
            if kb[0] == cid and extended[sel].test(set(kb[1]), True):
                implicatedSel = (KB[kb].getIdentifier() + extended[sel].getSPID())
                if implicatedSel in extended:
                    extended[implicatedSel] &= KB[kb]
                    if len(extended[implicatedSel]) == 0:
                        del extended[implicatedSel]
                else:
                    extended[implicatedSel] = KB[kb].copy()
                    extended[implicatedSel].setSPID(cpx[sel].getSPID())

    return extended

def Star(seed, negatives, ruleCover = []):
    print "Generating star"
    oT = time.time()
    dEvents = [{sel: seed[sel].copy()} for sel in seed if sel[:2] == 'd_']
    for neg in negatives:
        cover = []
        CDF = {}
        lookbackEvents = copy.deepcopy(dEvents)
        for sel in neg:
            if neg[sel].getSPID() == '0':
                if sel in seed and not neg[sel].test(seed[sel]):
                    extended = [{sel: neg[sel].getCompliment()}]
                    if extended not in cover:
                        cover.extend(extended)
            elif sel[:2] != 'd_':
                # Pick positives only for previous and differences
                lookbackEvents.extend([{sel: neg[sel].copy()}])
        cover.extend(multiply(lookbackEvents, cover))
        ruleCover = multiply(ruleCover, cover)
        if len(ruleCover) > 300:
            ruleCover = generalizeSimilarRules(ruleCover)

    iT = time.time()
    print "star complete, cover length : " + str(len(ruleCover))
    print "Time taken by star(" + str(len(negatives)) + "," + str(len(ruleCover)) + "): " + str(iT - oT)
    return ruleCover

ranks = []
proposedRule = []

def satisfyEvent(cpx, event):
    cpx = distanceKB(extendFromKB(cpx), filterOnly = False)
    stemCorrect = True
    predictionCorrect = False
    stemEvent = cpx.copy()
    predictionEvent = {}
    for key, sel in cpx.iteritems():
        if sel.getSPID() == "0" or key[:2] == "d_":
            predictionEvent[key] = stemEvent.pop(key)

    stemCorrect = True if multiply(stemEvent, event, lengthCheck=False) is not None else False
    if stemCorrect:
        predictionCorrect = True if multiply(predictionEvent, event, lengthCheck=False) is not None else False

    return (stemCorrect, predictionCorrect)

def isCoveredByProposed(event):
    for cpx in proposedRule:
        stemCorrect, predictionCorrect = satisfyEvent(cpx, event)
        if stemCorrect and predictionCorrect:
            return True
    return False

def generalizeSimilarRules(cover):
    print "generalization start (" + str(len(cover)) + ")"
    oT = time.time()
    newCover = []

    for i in range(0, len(cover)):
        if cover[i] is None:
            continue

        merged = copy.deepcopy(cover[i])
        rule = extendFromKB(cover[i])
        # rule = cover[i]

        for j in range(i + 1, len(cover)):
            if cover[j] is None:
                continue

            cRule = extendFromKB(cover[j])
            # cRule = cover[j]
            dist = 0
            keys = set(rule.keys()).union(cRule.keys())

            for sel in keys:
                SIR = sel in rule
                SIC = sel in cRule
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
                dist += (selDist * hammingVector[sel]) if sel in hammingVector else selDist

                if (dist > threshold["sameRuleDistance"]):
                    break

            if (dist <= threshold["sameRuleDistance"]):

                for key, sel in merged.iteritems():
                    if key in cover[j]:
                        sel |= cover[j].pop(key)
                merged.update(cover[j])
                cover[j] = None

        pSelPresent = False

        for key in merged.keys():
            if float(len(merged[key]))/float(len(merged[key].getDomain())) >= 0.8:
                del merged[key]
            elif not pSelPresent and merged[key].getSPID() == "0":
                pSelPresent = True

        if pSelPresent:
            newCover.append(merged)
    iT = time.time()
    print "Time taken by generalizeSimilarRules(" + str(len(newCover)) + "): " + str(iT - oT)
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
        pLen = 0
        nLen = 0
        pCover = []
        nCover = []
        for event in pos:
            stemCorrect, ruleSatisfy = satisfyEvent(rule, event)
            if stemCorrect:
                pLen += 1
                if ruleSatisfy:
                    pCount = pCount + 1
                    pCover.append(event)

        for event in neg:
            stemCorrect, ruleSatisfy = satisfyEvent(rule, event)
            if stemCorrect:
                nLen += 1
                if ruleSatisfy:
                    nCount = nCount + 1
                    nCover.append(event)

        domainCover = 1
        pRatio = 0
        nRatio = 0

        if not testingPhase:
            suits = len(rule['suit0']) if 'suit0' in rule else 4
            values = len(rule['value0']) if 'value0' in rule else 13
            domainCover = round(float(suits * values)/52.0,3)
            pRatio = round(float(pCount)/pLen,3) if pLen > 0 else threshold["positives"]
            nRatio = round(float(nCount)/nLen,3) if nLen > 0 else threshold["negatives"]
        else:
            # nCount = nCount - (rankedCpx[0][1] * lastEventSet[1])
            # nLen = nLen + lastEventSet[1]
            nRatio = round((float(nCount)/nLen + rankedCpx[0][1])/2 if nLen > 0 else (rankedCpx[0][1] * 1.2), 3)

            if nRatio == 0:                                 #If negative cover is 0.0, Do not let rule rank be affected by play bias
                pRatio = rankedCpx[0][0]
                pCount += rankedCpx[0][2]
            else:
                pRatio = round((float(pCount)/pLen + rankedCpx[0][0])/2 if pLen > 0 else (rankedCpx[0][0] * 0.8), 3)

            domainCover = -rankedCpx[0][3]

        rank.append(((pRatio, -nRatio, pCount, -domainCover), rule, (pCover, nCover)))

    rank.sort(key=lambda x: x[0], reverse=True)

    return rank

def LEF(cover, pos, neg, MAXSTAR=6, incrementing=False):
    print "LEF start"
    cover = generalizeSimilarRules(cover)
    oT = time.time()
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
    positives = []

    while neg:
        negatives.append(neg[0:4])
        neg = neg[4:]

    while pos:
        positives.append(pos[0:4])
        pos = pos[4:]

    while positives:
        pos = positives.pop()

        while negatives:
            neg = negatives.pop()
            covers = []

            print "\nAQ new event set iteration\n"
            if len(ranks) > 0:
                incrementalUpdate(ranks, pos, neg, lastEventSet)

            for seed in pos:
                if isCoveredByProposed(seed):
                    print "seed covered"
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

