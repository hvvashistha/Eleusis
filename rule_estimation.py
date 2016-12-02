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
    ("suit", ("C")): Selector("color", Selector.CIRCULAR, Card.domain["color"], '==', "B"),
    ("suit", ("B")): Selector("color", Selector.CIRCULAR, Card.domain["color"], '==', "B"),
    ("suit", ("D")): Selector("color", Selector.CIRCULAR, Card.domain["color"], '==', "R"),
    ("suit", ("H")): Selector("color", Selector.CIRCULAR, Card.domain["color"], '==', "R"),
    ("color", ("B",)): Selector("suit", Selector.CIRCULAR, Card.domain["suit"], '==', ["C", "S"]),
    ("color", ("R",)): Selector("suit", Selector.CIRCULAR, Card.domain["suit"], '==', ["D", "H"]),
    ("parity", (0,)): Selector("value", Selector.INTERVAL, Card.domain["value"], '==', [2, 4, 6, 8, 10 ,12]),
    ("parity", (1,)): Selector("value", Selector.INTERVAL, Card.domain["value"], '==', [1, 3, 5, 7, 9 ,11, 13]),
    ("value", (2, 4, 6, 8, 10 ,12)): Selector('parity', Selector.NOMINAL, [0, 1], '==', [0]),
    ("value", (1, 3, 5, 7, 9 ,11, 13)): Selector('parity', Selector.NOMINAL, [0, 1], '==', [1])
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
    "domainCover": -0.4
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

    # Following converts continuous range to (start..end) form
    #
    # if type == Selector.INTERVAL and len(newCover) > 0:
    #     originalCover = newCover
    #     newCover = []
    #     index = 0
    #     counter = 0
    #     for i in range(1, len(originalCover)):

    #         if originalCover[i] - originalCover[i-1] == 1:
    #             counter = counter + 1

    #         if originalCover[i] - originalCover[i-1] > 1:
    #             if counter < 2:
    #                 newCover = newCover + originalCover[index: index+counter + 1]
    #             else:
    #                 newCover.append((originalCover[index], originalCover[index+counter]))
    #             index = i
    #             counter = 0
    #     if counter < 2:
    #         newCover = newCover + originalCover[index: index+counter + 1]
    #     else:
    #         newCover.append((originalCover[index], originalCover[index+counter]))

    return newCover

def conjunct(cp1, cp2, referenceConjuctionCheck=False):
    if isinstance(cp1, list) and isinstance(cp2, list):     #Conjunction of OR
        conjunction = []

        for cpx1 in cp1:
            for cpx2 in cp2:
                conjunctedCpx = conjunct(cpx1, cpx2)
                if conjunctedCpx is not None and conjunctedCpx not in conjunction:
                    conjunction.append(conjunctedCpx)

        return conjunction or cp1 or cp2

    elif isinstance(cp1, dict) and isinstance(cp2, dict):   #Conjunction of AND
        conjunction = {}
        refConjuncted = False

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

            refConjuncted = eRef1 != eRef2

            newRef = list(eRef1.intersection(eRef2))

            if len(newRef) == 0:
                if referenceConjuctionCheck:
                    return None, None
                else:
                    return None

            selector.setReference(newRef)
            conjunction[i] = selector

        for i in cp1n2:
            conjunction[i] = cp1[i]

        for i in cp2n1:
            conjunction[i] = cp2[i]

        if referenceConjuctionCheck:
            return conjunction, refConjuncted
        return conjunction
    else:
        raise TypeError("Type of two complexes should be same. dict() for ANDed complexes, list() for ORed complexes")

def filterAndExtendFromKB(cpx):
    disjuncts = {}
    ruleSet = {}
    # print "->",
    # printDesc(cpx)
    for sel in cpx:
        try:
            cid = cpx[sel].getIdentifier()
        except:
            pdb.set_trace()

        cover1 = ruleSet[sel] if sel in ruleSet else None
        cover2 = cpx[sel]

        ruleSet, conjuncted = conjunct(ruleSet, {sel: cpx[sel]}, True)

        if ruleSet is None:
            break

        if conjuncted:
            sc1 = set(cover1.getExpandedReference())
            sc2 = set(cover2.getExpandedReference())
            s1 = copy.deepcopy(cover2)
            s1.setReference(list(sc1.intersection(sc2)))
            s2 = copy.deepcopy(cover2)
            s2.setReference(list(sc2 - sc1.intersection(sc2)))
            if len(s1.getExpandedReference()) > 0 and len(s2.getExpandedReference()) > 0:
                del ruleSet[sel]
                disjuncts[sel] = [s1, s2]

        for kb in KB:
            if kb[0] == cid and cpx[sel].test(list(kb[1]), True):
                kbImplication = copy.deepcopy(KB[kb])
                kbImplication.setSPID(cpx[sel].getSPID())
                cover2 = kbImplication

                ruleSet, conjuncted = conjunct(ruleSet, {(KB[kb].getIdentifier() + cpx[sel].getSPID()) : kbImplication}, True)

                if ruleSet is None:
                    break

                if conjuncted:
                    sc1 = set(cover1.getExpandedReference())
                    sc2 = set(cover2.getExpandedReference())
                    s1 = copy.deepcopy(cover1)
                    s1.setReference(list(sc1.intersection(sc2)))
                    s2 = copy.deepcopy(cover1)
                    s2.setReference(list(sc1 - sc1.intersection(sc2)))
                    if len(s1.getExpandedReference()) > 0 and len(s2.getExpandedReference()) > 0:
                        del ruleSet[sel]
                        disjuncts[sel] = [s1, s2]

    rule = []
    if ruleSet is not None:
        rule = [ruleSet]
        for name in disjuncts:
            intermediateRule = []
            for sel in disjuncts[name]:
                for ruleComplex in rule:
                    intermediateRule.extend(filterAndExtendFromKB(conjunct(ruleComplex, {name: sel})))
            rule = intermediateRule

    # print "<-",
    # printDesc(rule)
    return rule

def Star(seed, negatives):
    ruleCover = []
    n, i = 0,0
    for neg in negatives:
        n = n + 1
        cover = []
        CDF = {}
        for sel in neg:
            i = i + 1
            if not neg[sel].test(seed[neg[sel].getName()]):
                selector = copy.deepcopy(neg[sel])
                selector.setReference(getComplimentaryReference(selector.getType(), selector.getDomain(), removeCover=selector.getReference()))
                extended = filterAndExtendFromKB({sel: selector})
                if extended is not None and extended not in cover:
                    cover.extend(extended)
            # print "\n" + str(n) + "N, " + str(i) + "S>",
            # printDesc(neg[sel], newLine = False)
            # printDesc(cover, "=> Cover: ", False)

        # printDesc(cover, "Neg compliment Cover: ")
        ruleCover = [] or conjunct(ruleCover, cover)
        # printDesc(ruleCover, "Conjuncted: ")

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
                selDist = 0
                SIR = sel in rule
                identifier = rule[sel].getIdentifier() if SIR else cRule[sel].getIdentifier()
                domain = rule[sel].getExpandedDomain() if SIR else cRule[sel].getExpandedDomain()
                ruleRef = set(rule[sel].getExpandedReference() if SIR else domain)
                cRuleRef = set(cRule[sel].getExpandedReference() if sel in cRule else domain)
                selDist = 1.0 - float(len(ruleRef.intersection(cRuleRef)))/float(len(ruleRef.union(cRuleRef)))
                if identifier in hammingVector:
                    selDist = selDist * hammingVector[identifier]
                dist = dist + selDist

            if (dist <= threshold["sameRuleDistance"]):
                # print "\nSimilar! (" + str(dist) + ") >"
                # printDesc(cover[i])
                # printDesc(cover[j])
                similars = similars.union([j])
                covered = covered.union([j])

        ruleMergeList.append(similars)

    for rSet in ruleMergeList:
        similars = list(rSet)
        merged = cover[similars[0]]
        # print "\n\n merging"
        # printDesc(merged)
        for i in range(1, len(similars)):
            nRule = cover[similars[i]]
            # printDesc(nRule)
            for sel in nRule:
                if sel in merged:
                    uRef = list(set(merged[sel].getExpandedReference()).union(nRule[sel].getExpandedReference()))
                    uRef.sort()
                    merged[sel].setReference(uRef)
        # printDesc(merged, "Merged rule >")
        merged = filterAndExtendFromKB(merged)
        for r in merged:
            if r not in newCover:
                newCover.append(r)

    return newCover

def addRankVectors(rules, pos, neg):
    rank = []
    for rule in rules:
        pCount = 0
        nCount = 0
        for event in pos:
            if satisfyEvent(rule, event):
                pCount = pCount + 1

        for event in neg:
            if satisfyEvent(rule, event):
                nCount = nCount + 1

        suits = 4
        values = 13
        for sel in rule:
            if sel == 'suit0':
                suits = len(rule[sel].getReference())
            elif sel == 'value0':
                values = len(rule[sel].getReference())
        domainCover = round(float(suits * values)/52.0,3)

        pRatio = round(float(pCount)/len(pos),3)
        nRatio = round(float(nCount)/len(neg),3)

        rank.append(((pRatio, -nRatio, -domainCover), rule))

    return rank

def LEF(cover, pos, neg, MAXSTAR=4):
    cover = generalizeSimilarRules(cover)

    rank = addRankVectors(cover, pos, neg)

    if len(rank) > 0:
        rank.sort(reverse=True)
        print "all rules: (only top " + str(min(len(rank), MAXSTAR)) + " and those respecting threshold values are taken forward"
        print "Maximize -> (correct_positives/total_positives, correct_negatives/total_negatives, domain_cover)\n"
        for r in rank:
            print str(r[0]) + " : ",
            printDesc(r[1])

        rank = filter(
            lambda x: x[0][0] >= threshold["positives"] and x[0][1] >= threshold["negatives"] and x[0][2] >= threshold["domainCover"],
            rank)

        rank = rank[:min(len(rank), MAXSTAR)]

        print "\nRules picked from the list >"
        for r in rank:
            print str(r[0]) + " : ",
            printDesc(r[1])
        print ''
    return rank

## Generate a cover of all positives, so that no negative is covered
def AQ(pos, neg):
    covers = []
    ranks = []
    print "\nAQ new event set iteration\n"
    if len(proposedRule) > 0:
        print "Testing proposals on new events\n"
        rank = addRankVectors(proposedRule, pos, neg)
        rank.sort(reverse=True)
        for r in rank:
            print str(r[0]) + " : ",
            printDesc(r[1])
        print "--\n"

    for seed in pos:
        # printDesc(seed, 'Picking up seed>')
        if isCoveredByProposed(seed):
            printDesc(seed, "following seed already covered by proposed rules : ", False)
            print ''
            # print "Seed already covered by proposed rule"
            continue
        print "\nGenerating Cover"
        cover = Star(seed, neg)
        print "Cover generated\n"
        print "Doing Lexicographic evaluation----------->\n"
        seedRank = LEF(cover, pos, neg)
        print "Evaluation done!!<-----------\n"

        ranks.extend(seedRank)
        for i in seedRank:
            proposedRule.append(i[1])
    ranks.sort(reverse=True)

##################

def emulate_Play(numberOfPlayers = 6):
    rule = sys.argv[2]
    numberOfPlays = 10
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
        print "\n\nNew round of cards:\n"
        game.printRecord(numberOfPlayers + 1)
        eventSets['positive'] = eventSets['positive'] + pos
        eventSets['negative'] = eventSets['negative'] + neg
        # printDesc(pos, 'Positive Events>')
        # printDesc(neg, 'Negative Events>')
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

