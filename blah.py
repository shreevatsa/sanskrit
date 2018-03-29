# -*- coding: utf-8 -*-

"""
# An analysis of the Śloka metre as inferred from the text of the Mahābhārata

What can we infer about the *śloka* metre as used in the *Mahābhārata*, purely
from the text itself?

[
We would like to use only the text itself, without relying on the tradition of
Sanskrit prosody (*chandaḥśāstra*). The purpose is not to reject the tradition,
but instead that:

 1. Doing so can give us some confidence in our algorithms. If we program the
    rules of prosody into the computer, and the computer simply reproduces
    them, it can be unclear whether anything useful has been learned.

 2. It points to what a good reader/student could internalize/learn from simply
    reading and enjoying Sanskrit literature, without first approaching it via
    grammar and other such *śāstra*-s.
]

So let's do the analysis. We download MBH1-18U.HTM from GRETIL, and start
working on it. After removing some lines of the header, the trailing <BR> at
the end of each line, and some lines that mark the end of each of the 18
*parvan*-s of the Mahābhārata, we are left with a bunch of lines like (picking
somewhat at random):

...
03,149.013a	na hi śaknomi tvāṃ draṣṭuṃ divākaram ivoditam
03,149.013c	aprameyam anādhṛṣyaṃ mainākam iva parvatam
...
07,144.011a	tato 'sya saśaraṃ cāpaṃ muṣṭideśe sa cicchide
07,144.011c	dhvajaṃ ca tvaritaṃ chittvā rathād bhūmāv apātayat
...
08,031.067d*0423_01	yatra kṛṣṇārjunau vīrau yatra rājā yudhiṣṭhiraḥ
08,031.067d*0423_02	tatra dharmaś ca satyaṃ ca yato dharmas tato jayaḥ
...
12,313.001a	tataḥ sa rājā janako mantribhiḥ saha bhārata
12,313.001c	puraḥ purohitaṃ kṛtvā sarvāṇy antaḥpurāṇi ca
...
13,150.009d@020_0171	loke 'smin nāstikāḥ ke cin mūrkhāḥ paṇḍitamāninaḥ
13,150.009d@020_0172	bhrāmayanti ca te buddhiṃ cakrārūḍha ivekṣaṇam
...

The first step is to split each of these lines into an identifier and the
actual text.
"""

def split(line):
    """Given a line of the MBh text (from GRETIL), split it into
    an identifier (śloka part number) and the actual text."""
    line = line.strip()
    if not line: return None
    if '\t' in line:   parts = line.split('\t')
    elif '<>' in line: parts = line.split('<>')
    else:              parts = line.split(' ', maxsplit=1)
    assert len(parts) == 2, line
    return parts

"""
For each line's text, we can perform transliteration and scansion. Then we can enumerate the frequencies of the line lengths, and the patterns therein.
We can also keep 100 random samples for each.
"""

def add_to_sample(sample, instance, size=1000):
    import random
    sample.append(instance)
    while len(sample) > size:
        i = random.randrange(len(sample))
        sample.pop(i)

def get_patterns(filename):
    import pickle
    try:
        lengths, patterns, samples = pickle.load(open(filename + '.pickle', 'rb'))
        return lengths, patterns, samples
    except Exception as e:
        print(e)
    import scan
    from transliteration.transliterator import Transliterate
    from transliteration.transliterate import _IAST_TO_SLP1_STATE_MACHINE
    from collections import Counter, defaultdict
    lengths = Counter()
    patterns = Counter()
    samples = defaultdict(list)
    for (i, line) in enumerate(open(filename).readlines()):
        text = split(line)
        if text is None: continue
        line_id, text = text
        # Some obviously non-metrical lines: "vaiśaṃpāyana uvāca" etc.
        if len(text.split()) == 2 and text.split()[1] == 'uvāca':
            continue
        (trans, unused_unparsed) = Transliterate(_IAST_TO_SLP1_STATE_MACHINE, text)
        scanned = scan.ScanVerse([trans])
        assert len(scanned) == 1
        scanned = scanned[0]
        # if len(scanned) > 30:
        #     print(len(scanned), scanned, text)
        #     continue
        lengths[len(scanned)] += 1
        if len(scanned) == 16:
            patterns[scanned] += 1
            add_to_sample(samples[scanned], text)
        if i % 10000 == 0: print('Done until line %d' % i)
    pickle.dump((lengths, patterns, samples), open(filename + '.pickle', 'wb'))
    return lengths, patterns, samples

lengths, patterns, samples = get_patterns('MBH1-18U.HTM')
print('Got lengths, patterns, samples from MBH1-18U.')

"""
This is the distribution of lengths, in order of length:

Counter({0: 31,
         1: 1,
         2: 434,
         3: 226,
         4: 596,
         5: 490,
         6: 101,
         7: 83,
         8: 693,
         9: 108,
         10: 88,
         11: 4387,
         12: 1502,
         13: 168,
         14: 157,
         15: 132,
         16: 197727,
         17: 762,
         18: 107,
         19: 127,
         20: 99,
         21: 118,
         22: 7051,
         23: 1136,
         24: 1165,
         25: 184,
         26: 159,
         27: 49,
         28: 51,
         29: 22,
         30: 42,
         31: 15,
         32: 13,
         33: 15,
         34: 10,
         35: 2,
         36: 6,
         37: 7,
         38: 5,
         39: 6,
         40: 5,
         41: 3,
         42: 5,
         43: 2,
         44: 1,
         45: 2,
         46: 1,
         47: 3,
         48: 1,
         49: 2,
         50: 3,
         51: 1,
         52: 1,
         53: 2,
         54: 1,
         55: 3,
         56: 1,
         58: 1,
         60: 1,
         61: 2,
         66: 1,
         70: 2,
         77: 1,
         84: 1,
         87: 1,
         132: 1,
         146: 1,
         183: 1,
         221: 1})

In order of frequency:

[(16, 197727),
 (22, 7051),
 (11, 4387),
 (12, 1502),
 (24, 1165),
 (23, 1136),
 (17, 762),
 (8, 693),
 (4, 596),
 (5, 490),
 (2, 434),
 (3, 226),
 (25, 184),
 (13, 168),
 (26, 159),
 (14, 157),
 (15, 132),
 (19, 127),
 (21, 118),
 (9, 108),
 (18, 107),
 (6, 101),
 (20, 99),
 (10, 88),
 (7, 83),
 (28, 51),
 (27, 49),
 (30, 42),
 (0, 31),
 (29, 22),
 (33, 15),
 (31, 15),
 (32, 13),
 (34, 10),
 (37, 7),
 (36, 6),
 (39, 6),
 (38, 5),
 (42, 5),
 (40, 5),
 (47, 3),
 (55, 3),
 (41, 3),
 (50, 3),
 (35, 2),
 (70, 2),
 (61, 2),
 (43, 2),
 (49, 2),
 (53, 2),
 (45, 2),
 (48, 1),
 (58, 1),
 (132, 1),
 (87, 1),
 (54, 1),
 (84, 1),
 (183, 1),
 (146, 1),
 (51, 1),
 (44, 1),
 (77, 1),
 (60, 1),
 (46, 1),
 (52, 1),
 (221, 1),
 (66, 1),
 (56, 1),
 (1, 1)]

So we see that length-16 lines are the most common (28 times more common than the second most common, which is length 22 corresponding to upajāti/triṣṭubh), and account for 197727 or over 90% of the total number of lines. Here's a picture:

[lengths.png]
"""

import matplotlib.pyplot as plt
plt.close()
plt.plot([v for (k,v) in lengths.most_common()])
plt.ylabel('Frequency')
plt.xlabel('Rank among lengths')
plt.savefig('lengths.png')
print('Plotted lengths.png')
"""

Let's turn our focus to these length-16 lines, and examine the actual patterns (of Ls and Gs) found in those lines.

len(patterns) gives 1760, which is already meaningful despite the noise: it shows that these lines are metrical, because 1760 << 2^16 = 65536. If the lines were composed at random we would expect a significant larger fraction of the set of all possible patterns to arise, but instead less than 3% of the possible patterns are found. (In fact the true number is even less.) Here's a plot of the frequencies:

[patterns-16.png]
"""
plt.close()
plt.plot([v for (k,v) in patterns.most_common()])
plt.ylabel('Frequency')
plt.xlabel('Rank among patterns')
plt.savefig('patterns-16.png')

"""
and on a logarithmic scale:

[patterns-16-log.png]
"""
plt.yscale('log')
plt.savefig('patterns-16-log.png')
print('Plotted patterns-16.png and patterns-16-log')
"""
Now we know that every length-16 ardha of anuṣṭubh is made of two length-8 pādas. Do the odd pāda and even pāda behave independently, or is there some correlation between them? This is the first question. One way to answer it is to “factor” the length-16 lines into two halves and count the frequencies of the halves separately, then “multiply” the two counters and see if we get the same (relative) frequencies as before.
"""

def factor(counter):
    """Factor a counter that maps strings to integers, into two counters that map half-strings to counters."""
    from collections import Counter
    counter_odd = Counter()
    counter_even = Counter()
    for p in counter:
        n = len(p)
        assert n % 2 == 0
        m = n // 2
        counter_odd[p[:m]] += counter[p]
        counter_even[p[m:]] += counter[p]
    return counter_odd, counter_even

patterns_odd, patterns_even = factor(patterns)

def multiply(counter1, counter2):
    from collections import Counter
    counter = Counter()
    sum1 = sum(counter1.values())
    for p1 in counter1:
        for p2 in counter2:
            counter[p1 + p2] += (counter1[p1] * counter2[p2]) / sum1
    for k in counter:
        counter[k] = int(counter[k])
    return counter

patterns_multiplied = multiply(patterns_odd, patterns_even)
print('Factored and multiplied')

"""
This is what the two sequences look like:

Original:

 ('GLGGLGGGGLGGLGLG', 2530),     1
 ('GLGGLGGGGGGGLGLG', 2025),     2
 ('GGGGLGGGGLGGLGLG', 1906),     3
 ('GGGGLGGGGGGGLGLG', 1818),     5
 ('GLGLLGGGGLGGLGLG', 1668),     4
 ('GLGGLGGGGLGLLGLG', 1603),     8
 ('LGGGLGGGGLGGLGLG', 1580),     6
 ('GLGGLGGGLGGGLGLG', 1468),     7
 ('GLGGLGGGGGGLLGLG', 1449),     9
 ('LLGGLGGGGLGGLGLG', 1375),    10
 ...

Multiplied:

 ('GLGGLGGGGLGGLGLG', 2439),
 ('GLGGLGGGGGGGLGLG', 2010),
 ('GGGGLGGGGLGGLGLG', 1898),
 ('GLGLLGGGGLGGLGLG', 1592),
 ('GGGGLGGGGGGGLGLG', 1564),
 ('LGGGLGGGGLGGLGLG', 1550),
 ('GLGGLGGGLGGGLGLG', 1546),
 ('GLGGLGGGGLGLLGLG', 1524),
 ('GLGGLGGGGGGLLGLG', 1423),
 ('LLGGLGGGGLGGLGLG', 1381),
 ...

Let's plot the two.
"""

keys = [k for (k,v) in patterns_multiplied.most_common() if v > 0]
values1 = [patterns[k] for k in keys]
values2 = [patterns_multiplied[k] for k in keys]
assert len(values1) == len(keys) == len(values2)

plt.close()
plt.plot(values1, linestyle='None', marker='.', label='Original')
plt.plot(values2, linestyle='None', marker='.', label='Multiplied')
plt.legend(loc='upper right')
plt.savefig('patterns-16-compare.png')
plt.close()
plt.yscale('log')
plt.plot(values1, linestyle='None', marker='.', label='Original')
plt.plot(values2, linestyle='None', marker='.', label='Multiplied')
plt.legend(loc='upper right')
plt.savefig('patterns-16-compare-log.png')
print('Plotted comparisons')

"""
[patterns-16-compare.png]
[patterns-16-compare-log.png]

As we can see, the agreement is reasonably good (barring a couple of outliers that may merit further investigation), which suggests that we can indeed “factor” and look at the odd and even pāda-s separately. (In the code, see variables patterns_odd and patterns_even at this point.)
"""

plt.close()
plt.plot([v for (k,v) in patterns_odd.most_common()])
plt.ylabel('Frequency')
plt.xlabel('Rank among patterns for odd pāda')
plt.savefig('patterns-8-odd.png')
plt.yscale('log')
plt.savefig('patterns-8-odd-log.png')
plt.close()
plt.plot([v for (k,v) in patterns_even.most_common()])
plt.ylabel('Frequency')
plt.xlabel('Rank among patterns for even pāda')
plt.savefig('patterns-8-even.png')
plt.yscale('log')
plt.savefig('patterns-8-even-log.png')
print('Plotted 8-odd and 8-even')

"""
The first thing we notice is that the odd pādas have a larger count of patterns that occur, and a gentler curve (a less steep downward slope). This indicates that the even śloka pādas are more regular than the odd ones.

The next question we ask is whether the last syllable (which is optionally treated as guru no matter the exact scansion) matters.
"""

def makeLastOptional(counter):
    from collections import Counter
    patterns_any = Counter()
    patterns_l = Counter()
    patterns_g = Counter()
    for key in counter:
        basic = key[:-1]
        patterns_any[basic] += counter[key]
        if key[-1] == 'L':
            patterns_l[basic] += counter[key]
        elif key[-1] == 'G':
            patterns_g[basic] += counter[key]
        else:
            assert False, key
    return (patterns_any, patterns_l, patterns_g)

patterns_odd_7_any, patterns_odd_7_l, patterns_odd_7_g = makeLastOptional(patterns_odd)
patterns_even_7_any, patterns_even_7_l, patterns_even_7_g = makeLastOptional(patterns_even)

keys = [k for (k,v) in patterns_even_7_any.most_common()]
values1 = [patterns_even_7_any[k] for k in keys]
values2 = [patterns_even_7_l[k] for k in keys]
values3 = [patterns_even_7_g[k] for k in keys]
plt.close()
plt.plot(values3, linestyle='-', marker='.', label='guru')
plt.plot(values2, linestyle='-', marker='.', label='laghu')
plt.plot(values1, linestyle='-', marker='.', label='Any')
# plt.setp(plt.get_xticklabels(), rotation=90, horizontalalignment='right')
# plt.xlabel('patterns', family='monospace')
plt.tick_params(axis='x', labelsize=4)
locs, labels = plt.xticks(range(len(keys)), keys, family='monospace')
plt.setp(labels, rotation=90)
plt.legend(loc='upper right')
print('Saving patterns-even-7.png')
plt.savefig('patterns-even-7.png', dpi=600)

"""
These are the most common:

In [574]: blah.patterns_even_7_any.most_common()
Out[574]:
[('GLGGLGL', 33762),
 ('GGGGLGL', 28452),
 ('LGGGLGL', 21779),
 ('GLGLLGL', 21107),
 ('GGGLLGL', 20297),
 ('LLGGLGL', 19080),
 ('GGLLLGL', 16198),
 ('LGGLLGL', 15649),
 ('LGLLLGL', 10996),
 ('LLGLLGL', 9969),
 ('LGLGLGL', 126),
 ('GGGGGGL', 51),
 ('GGLGLGL', 49),
 ('GLGGGGL', 31),
 ('LLGGGGL', 27),
 ('LGGGGGL', 24),
 ('GGLLGGL', 13),
 ('GLLLLGL', 12),
 ('LGLLGGL', 11),
 ('GGGLGGL', 10),
 ('GLGLGGL', 6),
 ('GGGGLGG', 5),
 ('LGGLGGL', 5),
 ('GLGGLGG', 3),
 ('LLLGLGL', 3),
 ('GLLGLGL', 3),
 ('LLLLLGL', 3),
 ('GGLGLGG', 2),
 ('GGGGGLG', 2),
 ('GGGLGGG', 2),
 ('GLGGGLL', 2),
 ('GGLLGLG', 2),
 ('GGGGLLL', 2),
 ('GLGLLGG', 2),
 ('LLGGLGG', 2),
 ('LGGLGGG', 2),
 ('LGLLGLL', 2),
 ('LGGGLLL', 2),
 ('GLGLLLL', 2),
 ('GGLGGLG', 2),
 ('LGGGLGG', 2),
 ('GGGGGGG', 2),
 ('LLGLGLL', 1),
 ('LGGGGGG', 1),
 ('LGLGLLG', 1),
 ('GLLGGLL', 1),
 ('LGGLLLL', 1),
 ('GLGGGLG', 1),
 ('GLLGLGG', 1),
 ('LLGGLLL', 1),
 ('LGGLGLG', 1),
 ('GGGLLGG', 1),
 ('LGGLLGG', 1),
 ('GGLLLLL', 1),
 ('LLGLGGL', 1),
 ('GGLLGGG', 1),
 ('GLGGLLL', 1),
 ('GGLLLGG', 1),
 ('GLLGLLL', 1),
 ('GGLLLLG', 1),
 ('LGLGGLL', 1),
 ('LGGLGLL', 1),
 ('LGGLLLG', 1),
 ('LLLGGGL', 1),
 ('LGGGGLG', 1),
 ('GGLGGGG', 1),
 ('LLLGLGG', 1),
 ('LGLLGLG', 1)]

That's 68 out of a possible 128.

These are the counts for all possible 2^4=16 possibilities for the first 4 characters when followed by LGL (for even pādas of śloka):

LLLL 3
LLLG 3
LLGL 9969
LLGG 19080
LGLL 10996
LGLG 126
LGGL 15649
LGGG 21779
GLLL 12
GLLG 3
GLGL 21107
GLGG 33762
GGLL 16198
GGLG 49
GGGL 20297
GGGG 28452

Here they are again, sorted, and with a list of positions i such that syllables (i, i+1) are both L:

GLGG-LGL. 33762  -
GGGG-LGL. 28452  -
LGGG-LGL. 21779  -
GLGL-LGL. 21107  4
GGGL-LGL. 20297  4
LLGG-LGL. 19080  1
GGLL-LGL. 16198  3
LGGL-LGL. 15649  4
LGLL-LGL. 10996  3,4
LLGL-LGL. 9969   1,4

LGLG-LGL. 126    - (but pramāṇikā)
GGLG-LGL. 49     - (but pramāṇikā)
GLLL-LGL. 12     2,3,4
LLLL-LGL. 3      1,2,3,4
LLLG-LGL. 3      1,2
GLLG-LGL. 3      2

As we can see, there's a clear gap between the 10 possibilities that occur ~10000 times and the remaining 6 that barely occur at all. (And all the other of the 2^7 patterns that do not end with LGL. similarly occur <=51 times.)
The rules can be summarized as follows:
For an *even* pāda of śloka,
- syllables 5, 6, 7 should be LGL
- syllables 2 and 3 should not both be LL
- syllables 2, 3, 4 should not be GLG, resulting in the metre becoming .GLGLGL. (the pramāṇikā pitfall)

This *can* be cast as a rule about the syllables 2,3,4, a gaṇa: of the 2^8 possible gaṇas, these 5 are allowed LGL (ja), LGG (ya), GLL (bha), GGL (ta), GGG (ma), while these 3 are disallowed: LLL (na), LLG (sa), GLG (ra). (And the syllables 5,6,7 are always LGL (ja).) But this rule, though easier to state, is harder to remember than the above formulation, and gives less of an insight into the nature of the constraints. For example, stating the rule about consecutive Ls in positions 2 and 3 shows why the ones without such a repetition (even in other positions than 2&3) are preferred over the ones with a repetition. (For example, why GLGL-LGL. 21107 is preferred over LLGL-LGL. 9969, even though the only difference is in the first syllable.)

Let's do the same for the odd pādas, which are more irregular in practice.
"""

keys = [k for (k,v) in patterns_odd_7_any.most_common()]
values1 = [patterns_odd_7_any[k] for k in keys]
values2 = [patterns_odd_7_l[k] for k in keys]
values3 = [patterns_odd_7_g[k] for k in keys]
plt.close()
plt.plot(values3, linestyle='-', marker='.', label='guru')
plt.plot(values2, linestyle='-', marker='.', label='laghu')
plt.plot(values1, linestyle='-', marker='.', label='Any')
# plt.setp(plt.get_xticklabels(), rotation=90, horizontalalignment='right')
# plt.xlabel('patterns', family='monospace')
plt.tick_params(axis='x', labelsize=4)
locs, labels = plt.xticks(range(len(keys)), keys, family='monospace')
plt.setp(labels, rotation=90)
plt.legend(loc='upper right')
print('Saving patterns-odd-7.png')
plt.savefig('patterns-odd-7.png', dpi=600)

"""
These are the most common (100 out of 128):

In [593]: blah.patterns_odd_7_any.most_common()
Out[593]:
[('GLGGLGG', 26934),
 ('GGGGLGG', 21478),
 ('LGGGLGG', 17051),
 ('GLGLLGG', 16761),
 ('LLGGLGG', 15272),
 ('GGGLLGG', 13404),
 ('GGLLLGG', 12112),
 ('LGGLLGG', 11512),
 ('LGLLLGG', 10054),
 ('LGLGLGG', 9493),
 ('GGLGLGG', 9490),
 ('LLGLLGG', 7696),
 ('LGLGGGG', 3956),
 ('GGLGGGG', 3448),
 ('GLGGLLL', 2758),
 ('LGLGGLL', 2748),
 ('GGLGGLL', 2674),
 ('GGGGLLL', 2073),
 ('LGGGLLL', 1650),
 ('LLGGLLL', 1196),
 ('LGLGLLL', 1167),
 ('GGLGLLL', 1162),
 ('LGLGGLG', 768),
 ('GGLGGLG', 700),
 ('GGGGGLG', 431),
 ('GLGGGLG', 290),
 ('LGGGGLG', 278),
 ('GGGGGLL', 191),
 ('LGGGGLL', 141),
 ('GLGGGLL', 137),
 ('LGLGLGL', 117),
 ('LLGGGLG', 74),
 ('GGGGGGG', 57),
 ('LGGGGGG', 49),
 ('GLGGGGG', 44),
 ('LLGGGLL', 38),
 ('LLGGGGG', 25),
 ('GLGLGGG', 22),
 ('GGGGLLG', 20),
 ('GGLLGGG', 17),
 ('LGLGLLG', 15),
 ('GLLGLGG', 15),
 ('LGGGLLG', 12),
 ('LLGLGGG', 11),
 ('GLGGLLG', 11),
 ('GLLLLGG', 10),
 ('GGGGLGL', 10),
 ('LLGGLLG', 9),
 ('LGLLGGG', 9),
 ('LGGLGGG', 8),
 ('GGLGLLG', 8),
 ('GGLGGGL', 6),
 ('GLGGLGL', 6),
 ('LLLLLGG', 5),
 ('GGGLGLL', 5),
 ('GGGLGGG', 5),
 ('LLLGLGG', 5),
 ('GGGLLLL', 5),
 ('GLGLLLG', 4),
 ('LLGLGLG', 4),
 ('LGLGGGL', 4),
 ('LLGGLGL', 4),
 ('GGGGGGL', 4),
 ('LGGGLGL', 3),
 ('GGGLLGL', 3),
 ('LGGLLGL', 3),
 ('LLGLGLL', 3),
 ('GGGLLLG', 3),
 ('LGLLLLG', 3),
 ('GLGGGGL', 2),
 ('LGLLGLG', 2),
 ('LLGLGGL', 2),
 ('GLLGGLL', 2),
 ('GLLGGLG', 2),
 ('LLLGGGG', 2),
 ('GGGLGLG', 2),
 ('LGGLLLG', 2),
 ('LLLLGGG', 2),
 ('GGLGLGL', 2),
 ('LLLGGGL', 2),
 ('LGGLLLL', 2),
 ('LLGLLGL', 2),
 ('GGLLGLL', 2),
 ('GGLLLLG', 2),
 ('GGGLGGL', 1),
 ('LLLGGLG', 1),
 ('GLGLLGL', 1),
 ('LGGLGGL', 1),
 ('LGGGGGL', 1),
 ('GLLGGGG', 1),
 ('LLGGGGL', 1),
 ('GGLLLGL', 1),
 ('GLLLLLL', 1),
 ('LLLGGLL', 1),
 ('GLLLLGL', 1),
 ('GLGLGLG', 1),
 ('LLLGLLL', 1),
 ('LGLLLGL', 1),
 ('GLGLLLL', 1),
 ('GGLLLLL', 1)]

The ones ending with LGG are most common again, so here's a list of all 2^4 = 16 patterns that end with LGG:

In [594]: [(k,v) for (k,v) in blah.patterns_odd_7_any.most_common() if k[-3:] == 'LGG']
Out[594]:
[('GLGGLGG', 26934),
 ('GGGGLGG', 21478),
 ('LGGGLGG', 17051),
 ('GLGLLGG', 16761),
 ('LLGGLGG', 15272),
 ('GGGLLGG', 13404),
 ('GGLLLGG', 12112),
 ('LGGLLGG', 11512),
 ('LGLLLGG', 10054),
 ('LGLGLGG', 9493),
 ('GGLGLGG', 9490),
 ('LLGLLGG', 7696),
 ('GLLGLGG', 15),
 ('GLLLLGG', 10),
 ('LLLLLGG', 5),
 ('LLLGLGG', 5)]

Note again that the four patterns that have LL in positions 2 and 3 are the least common.
The top 12 are also the top 12 overall. But the other 4 barely occur.

Of the ones that don't end with 'LGG.', there are the following:

In [613]: [(k,v) for (k,v) in blah.patterns_odd_7_any.most_common() if k[-3:] != 'LGG' and v > 60]
Out[613]:
[('LGLGGGG', 3956),
 ('GGLGGGG', 3448),
 ('GLGGLLL', 2758),
 ('LGLGGLL', 2748),
 ('GGLGGLL', 2674),
 ('GGGGLLL', 2073),
 ('LGGGLLL', 1650),
 ('LLGGLLL', 1196),
 ('LGLGLLL', 1167),
 ('GGLGLLL', 1162),
 ('LGLGGLG', 768),
 ('GGLGGLG', 700),
 ('GGGGGLG', 431),
 ('GLGGGLG', 290),
 ('LGGGGLG', 278),
 ('GGGGGLL', 191),
 ('LGGGGLL', 141),
 ('GLGGGLL', 137),
 ('LGLGLGL', 117),
 ('LLGGGLG', 74)]

The picture becomes clearer (or at least smaller!) if we further partition all these length-7 odd padas by ignoring the first syllable.
"""

def makeFirstOptional(counter):
    from collections import Counter
    patterns_any = Counter()
    patterns_l = Counter()
    patterns_g = Counter()
    for key in counter:
        basic = key[1:]
        patterns_any[basic] += counter[key]
        if key[1] == 'L':
            patterns_l[basic] += counter[key]
        elif key[1] == 'G':
            patterns_g[basic] += counter[key]
        else:
            assert False, key
    return (patterns_any, patterns_l, patterns_g)

patterns_odd_6_any, patterns_odd_6_l, patterns_odd_6_g = makeFirstOptional(patterns_odd_7_any)

"""
In [617]: [('x' + k + 'x', v) for (k, v) in blah.patterns_odd_6_any.most_common()]
Out[617]:
[('xLGGLGGx', 42206),
 ('xGGGLGGx', 38529),
 ('xGGLLGGx', 24916),
 ('xLGLLGGx', 24457),
 ('xGLLLGGx', 22166),
 ('xGLGLGGx', 18983),
 ('xGLGGGGx', 7404),
 ('xGLGGLLx', 5422),
 ('xLGGLLLx', 3954),
 ('xGGGLLLx', 3723),
 ('xGLGLLLx', 2329),
 ('xGLGGLGx', 1468),
 ('xGGGGLGx', 709),
 ('xLGGGLGx', 364),
 ('xGGGGLLx', 332),
 ('xLGGGLLx', 175),
 ('xGLGLGLx', 119),
 ('xGGGGGGx', 106),
 ('xLGGGGGx', 69),
 ('xLGLGGGx', 33),
 ('xGGGLLGx', 32),
 ('xGLLGGGx', 26),
 ('xGLGLLGx', 23),
 ('xLGGLLGx', 20),
 ('xLLGLGGx', 20),
 ('xLLLLGGx', 15),
 ('xGGLGGGx', 13),
 ('xGGGLGLx', 13),
 ('xGLGGGLx', 10),
 ('xLGGLGLx', 10),
 ('xGGLLLLx', 7),
 ('xGGLLGLx', 6),
 ('xLGLGLGx', 5),
 ('xGGLGLLx', 5),
 ('xGGLLLGx', 5),
 ('xGGGGGLx', 5),
 ('xGLLLLGx', 5),
 ('xLGLLLGx', 4),
 ('xLGGGGLx', 3),
 ('xLLGGLLx', 3),
 ('xLLGGLGx', 3),
 ('xLGLGLLx', 3),
 ('xLLGGGGx', 3),
 ('xLGLLGLx', 3),
 ('xGGLGGLx', 2),
 ('xGLLGLGx', 2),
 ('xLGLGGLx', 2),
 ('xGGLGLGx', 2),
 ('xLLLGGGx', 2),
 ('xGLLLGLx', 2),
 ('xLLGGGLx', 2),
 ('xGLLGLLx', 2),
 ('xLLLLLLx', 1),
 ('xLLLLGLx', 1),
 ('xLLGLLLx', 1),
 ('xLGLLLLx', 1),
 ('xGLLLLLx', 1)]

As expected, the 6 that end with LGGx *without* starting as xLL are most common, while the 2 that start as xLL and end as LGGx are not very common.
Here are some samples for each of the other common ones that don't end with 'LGGx':
"""

from collections import defaultdict
sixsamples = defaultdict(list)
for key in samples.keys():
    sixsamples[key[1:7]].extend(samples[key])

"""
The samples for GGGGGG are especially interesting, because they all appear to be instances of the "treat some guru as laghu" poetic license.

In [658]: blah.sixsamples['GGGGGG']
Out[658]:
 'ahaṃ te sarvaṃ bhaikṣaṃ gṛhṇāmi na cānyac carasi',           Occurs in 01,003.043B a nonmetrical portion.
 'tābhyām ābaddhābhyāṃ brāhmaṇān pariveṣṭum icchāmi',          Occurs in 01,003.100F a nonmetrical portion.
 'cakraṃ cāpaśyat ṣaḍbhiḥ kumāraiḥ parivartyamānam',           Occurs in 01,003.148B a nonmetrical portion.
 'tasmāj jyeṣṭhaś ca śreṣṭhaś ca pāṇḍur dharmabhṛtāṃ varaḥ',   k śreṣṭhaś, is GGGGLGGG ('xGGGLGGx', 38529)
 'tenābhidrutya kruddhena bhīmo mūrdhni samāhataḥ',            k kruddhena is GGGGLGGx ('xGGGLGGx', 38529)
 'ity ukte cāsyā jagrāha pāṇiṃ gālavasaṃbhavaḥ',               Feels wrong. Typo?
 'ity uktas tām uttaṅkas tu bhartur vākyam athābravīt',        Feels wrong.
 'āgneyāny atra kṣiptāni parito veśmanas tathā',               k kṣiptāni
 'tubhyaṃ niṣkaṃ tubhyaṃ niṣkam iti ha sma prabhāṣate',        Feels wrong.
 'grāhyaṃ dṛśyaṃ ca śrāvyaṃ ca yad idaṃ karma vidyate',        k śrāvyaṃ
 'jagāma bhrātṝn ādāya sarvān mātaram eva ca',                 k bhrātṝn
 'subhikṣaṃ rājyaṃ labdhaṃ vai vasiṣṭhasya tapobalāt',         Feels ok! LGG-G[G]-GGG
 'sahasraṃ vānaprasthānāṃ sahasraṃ gṛhamedhinām',              k prasthānāṃ
 'mahābhūtāni cchandāṃsi prajānāṃ patayo makhāḥ',              Typo?
 'samīpe tv agnīṣomābhyāṃ pitṛbhyo juhuyāt tathā',             Feels ok! LGG-G[G]-GGG
 'yathā kāmaś ca krodhaś ca nirjitāv ajitau naraiḥ',           k krodhaś
 'paristomāś ca prāsāś ca ṛṣṭayaś ca mahādhanāḥ',              k prāsāś
 'sainyaṃ sainyena vyūḍhena eka ekena vā punaḥ',               k vyūḍhena
 "uktaḥ skandena brūhīti so 'bravīd vāsavas tataḥ",            k brūhīti
 'jagmuḥ svāny eva sthānāni pūjayitvā jaleśvaram',             k sthānāni
 'evaṃ vipreṣu kruddheṣu devarājaḥ śatakratuḥ',                k kruddheṣu
 'hāniṃ vṛddhiṃ ca hrāsaṃ ca varṇasthānaṃ balābalam',          k hrāsaṃ
 'suprītas tāvat tiṣṭhasva yāvat karṇaṃ vadhāmy aham',         Feels ok! LGG-G[G]-GGG
 'sā śaptā tena kruddhena viśvāmitreṇa dhīmatā',               k kruddhena
 'dharmaḥ kāmaś ca svargaś ca harṣaḥ krodhaḥ śrutaṃ damaḥ',    k svargaś
 'gulāni svādukṣaudrāṇi dadus te brāhmaṇeṣv iha',              k svādukṣaudrāṇi
 'tato gaccheta brahmarṣer gautamasya vanaṃ nṛpa',             k brahmarṣer
 'ekībhūto hi srakṣyāmi śarīrād dvijasattama',                 k srakṣyāmi
 'kule jātāś ca kliśyante dauṣkuleyavaśānugāḥ |',              k kliśyante
 'avaśyaṃ cāpi draṣṭavyaḥ pāṇḍavaḥ puruṣarṣabhaḥ',             k draṣṭavyaḥ
 'kṛte tretādiṣv eteṣāṃ pādaśo hrasate vayaḥ',                 Feels ok! LG-GG[G]-GGG
 'turīyārdhena brahmāṇaṃ tasya viddhi mahātmanaḥ',             k brahmāṇaṃ
 'bhavān indradyumnaṃ rājānaṃ pratyabhijānātīti',              k dyumnaṃ in indradyumnaṃ?
 'āgneyaś caiva skandaś ca dīptakīrtir anāmayaḥ',              k skandaś
 'abhyāvarteta brahmāsya antarātmani vai śritam',              k brahmāsya
 'jānītām adya jyeṣṭhasya pāṇḍavasya parākramam',              k jyeṣṭhasya
 'ucchiṣṭaṃ vāpi cchidreṣu varjayanti tapodhanāḥ',             k cchidreṣu?
 'guṇāḥ svargasya proktās te doṣān api nibodha me',            k proktās
 'mama bhrātā ca nyāyyena tvayā rakṣyā mahāratha',             k bhrātā / nyāyyena
 'tadā dharmasya dvau pādāv adharmo nāśayiṣyati',              k dvau
 "śakro 'py āpṛcchya brahmāṇaṃ devarājyam apālayat",           k brahmāṇaṃ
 'āṣāḍhe māsi dvādaśyāṃ vāmaneti ca pūjayet',                  k dvādaśyāṃ
 'vinā sairandhrīṃ bhadraṃ te svayaṃ gandharvarakṣitām',       Feels ok? LG-GGG-GGG
 'svayaṃ krītāsu preṣyāsu prasūyante tu ye narāḥ',             k preṣyāsu
 'atikrāntaṃ ca prāptaṃ ca prayatnāc copapāditam',             k prāptaṃ
 'tyaktvā kāmaṃ sairandhryāṃ tvaṃ madīyāṃ dhvajinīṃ bhavān',   Feels wrong? GG-GG-GGG-G
 'anyac ca brūyāṃ rājendra pratijñāṃ mama nityadā',            k brūyāṃ
 "tato 'gniṃ tatra prajvālya darśayitvā tu kīcakam",           k prajvālya
 'hate bhīṣme ca droṇe ca sūtaputre ca pātite',                k droṇe
 'abhikruddhasya kruddhas tu tāḍayām āsa tāṃ gadām',           k kruddhas
 'ūrdhvaṃ prāṇā hy utkrāmanti yūnaḥ sthavira āyati',           Feels wrong? GG-GG-GGGG
 'prāptavyāny eva prāpnoti duḥkhāni ca sukhāni ca',            k prāpnoti
 'ūrdhvaṃ prāṇā hy utkrāmanti yūnaḥ sthavira āyati',           Feels wrong? GG-GG-GGGG same line as above
 'jñānaṃ vai nāma pratyakṣaṃ parokṣaṃ jāyate tapaḥ',           k pratyakṣaṃ
 'nāmāny etāni brahmarṣe śarīrasyeśvarasya vai',               k brahmarṣe
 'nāmāny etāni brahmarṣe śarīrasyeśvarasya vai',               k brahmarṣe
 'sauvarṇā yatra prāsādā vasor dhārāś ca kāmadāḥ',             k prāsādā
 'trigartānāṃ ca dvau mukhyau yau tau saṃśaptakāv iti',        k dvau
 "grasaty arkaṃ ca svarbhānur bhūtvā māṃ so 'bhirakṣatu",      k svarbhānur
 'yathā bhīṣmeṇa droṇena bāhlīkena ca dhīmatā',                k droṇena
 'hate bhīṣme ca droṇe ca karṇo jeṣyati pāṇḍavān',             k droṇe
 'hate bhīṣme ca droṇe ca karṇo jeṣyati pāṇḍavān',             k droṇe
 'hate bhīṣme ca droṇe ca karṇe caiva mahārathe',              k droṇe
 'laghutvaṃ caiva prāpnoti ājñā cāsya nivartate',              k prāpnoti
 'mayaitan nāma pradhyātaṃ manasā śocatā kila',                k pradhyātaṃ
 'mānena bhraṣṭaḥ svargas te nārhas tvaṃ pārthivātmaja',       k bhraṣṭaḥ
 'abhyāśe nityaṃ devānāṃ saptarṣīṇāṃ dhruvasya ca',            Feels ok-ish? GGG-G[G]-GGG
 'ghrāṇaṃ cakṣuś ca śrotraṃ ca tvag jihvā buddhir eva ca',     k śrotraṃ
 'karṇaṃ ca tvāṃ ca drauṇiṃ ca kṛpaṃ ca sumahāratham',         k tvāṃ / drauṇiṃ
 'tato bhīṣmaś ca droṇaś ca sainyena mahatā vṛtau',            k droṇaś
 "sthirā buddhir hi droṇasya na pārtho vakṣyate 'nṛtam",       k droṇasya
 'idānīm eva draṣṭāsi pradhane syandane sthitau',              k draṣṭāsi
 'gajacchāyāyāṃ pūrvasyāṃ kutupe dakṣiṇāmukhaḥ',               Feels ok? LGGG[G]-GGG
 'evaṃ hīneṣu vrātyeṣu bāhlīkeṣu durātmasu',                   k vrātyeṣu
 'tvaṃ hi draṣṭā ca śrotā ca kṛcchreṣv arthakṛteṣv iha',       k draṣṭā / śrotā
 'yat prāpya kleśaṃ nāpnoti tan me brūhi pitāmaha',            k kleśaṃ
 'yat prāpya kleśaṃ nāpnoti tan me brūhi pitāmaha',            k kleśaṃ
 'teṣāṃ dṛṣṭvā tu kruddhānāṃ vapūṃṣy amitatejasām',            k kruddhānāṃ
 'tasminn evāsṛksaṃklinne tad adbhutam ivābhavat',
 'te māṃ gāyanti prāgvaṃśe adhokṣaja iti sthitiḥ',
 'yathā bhrājanti syandantaḥ parvatā dhātumaṇḍitāḥ',
 'pitṝn devāṃś ca prīṇāti pretya cānantyam aśnute',
 'sa cāgastyena kruddhena bhraṃśito bhūtalaṃ gataḥ',
 'ahorātreṇa dvādaśyāṃ māghamāse tu mādhavam',
 'ahorātreṇa dvādaśyāṃ mārgaśīrṣe tu keśavam',
 'cāturvedyaṃ cāturhotraṃ cāturāśramyam eva ca',
 'naiva prāpnoti brāhmaṇyam abhidhyānāt kathaṃ cana',
 'arghyaṃ pādyaṃ ca nyāyena tayābhipratipāditaḥ',
 'śvitrī kuṣṭhī ca klībaś ca tathā yakṣmahataś ca yaḥ',
 'prāg garbhādhānān mantrā hi pravartante dvijātiṣu',
 'namo jyeṣṭhāya śreṣṭhāya balapramathanāya ca',
 'tat te dāsyāmi prītātmā matprasādo hi durlabhaḥ',
 'chatraṃ succhatro vikhyātaḥ sarvalokāśrayo mahān',
 'jihvābhir ye viṣvagvaktraṃ; lelihyante sūryaprakhyam',
 'bhaktyā devaṃ viśvotpannaṃ; yasmāt sarve lokāḥ sūtāḥ',
 'jñānāny etāni brahmarṣe lokeṣu pracaranti ha',
 'vaṣaṭkārāya svāhāya svadhāya nidhanāya ca',
 "śmaśāne kasya krīḍārthaṃ nṛtye vā ko 'bhibhāṣyate",
 'ahorātreṇa dvādaśyāṃ jyeṣṭhe māsi trivikramam',
 'tilādāne ca kravyādā ye ca krodhavaśā gaṇāḥ',
 'ahorātreṇa dvādaśyāṃ caitre viṣṇur iti smaran',
 'ṛgvedaṃ tena prīṇāti prathamaṃ yaḥ pibed apaḥ',
 'brahmāṇaṃ tena prīṇāti yan mūrdhani samāpayet',
 'tathety uktaś ca provāca bhagavāñ śaṃkaras tadā',
 'kiṃ vā dhyānena draṣṭavyaṃ yad bhavān anupaśyati',
 'ahorātreṇa dvādaśyāṃ śrāvaṇe māsi śrīdharam'

"""
