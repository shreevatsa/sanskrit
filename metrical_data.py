#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Data structures that store matching metres for known patterns."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
# import logging
import re

import match_result
import simple_utils


class AllMetricalData(object):
  """Known patterns and regexes, both full and partial."""

  # TODO(shreevatsa): Remove _init from these names
  def __init__(self, known_metre_patterns_init, known_metre_regexes_init,
               known_partial_patterns_init):
    self.known_metre_patterns = known_metre_patterns_init
    self.known_metre_regexes = known_metre_regexes_init
    self.known_partial_patterns = known_partial_patterns_init


known_metre_regexes = []
known_metre_patterns = {}
known_partial_regexes = []
known_partial_patterns = {}


def CleanUpPattern(pattern):
  pattern = simple_utils.RemoveChars(pattern, ' —–')
  assert re.match(r'^[LG]*$', pattern), pattern
  return pattern


def CleanUpSimpleRegex(regex):
  regex = simple_utils.RemoveChars(regex, ' —–')
  assert re.match(r'^[LG.]*$', regex), regex
  return regex


def AddSamavrttaPattern(metre_name, each_line_pattern):
  """Given a sama-vṛtta metre's pattern, add it to the data structures."""
  clean = CleanUpPattern(each_line_pattern)
  assert re.match(r'^[LG]*G$', clean), (each_line_pattern, metre_name)
  patterns = [clean[:-1] + 'G', clean[:-1] + 'L']
  for (a, b, c, d) in itertools.product(patterns, repeat=4):
    issues = ([match_result.ISSUES.VISAMA_PADANTA_LAGHU]
              if a.endswith('L') or c.endswith('L')
              else [])
    assert (a + b + c + d) not in known_metre_patterns
    known_metre_patterns[a + b + c + d] = match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.FULL, issues)
  for (a, b) in itertools.product(patterns, repeat=2):
    issues = ([match_result.ISSUES.VISAMA_PADANTA_LAGHU] if a.endswith('L')
              else [])
    assert a + b not in known_partial_patterns
    known_partial_patterns[a + b] = [match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.HALF, issues)]
  for a in patterns:
    issues = [match_result.ISSUES.PADANTA_LAGHU] if a.endswith('L') else []
    assert a not in known_partial_patterns
    known_partial_patterns[a] = [match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.PADA, issues)]


def AddArdhasamavrttaPattern(metre_name, odd_line_pattern, even_line_pattern):
  """Given an ardha-sama-vṛtta metres' pattern, add it."""
  clean_odd = CleanUpPattern(odd_line_pattern)
  assert re.match(r'^[LG]*G$', clean_odd)
  clean_even = CleanUpPattern(even_line_pattern)
  assert re.match(r'^[LG]*G$', clean_even)
  patterns_odd = [clean_odd[:-1] + 'G', clean_odd[:-1] + 'L']
  patterns_even = [clean_even[:-1] + 'G', clean_even[:-1] + 'L']
  for (a, b, c, d) in itertools.product(patterns_odd, patterns_even, repeat=2):
    issues = ([match_result.ISSUES.VISAMA_PADANTA_LAGHU]
              if a.endswith('L') or c.endswith('L')
              else [])
    assert (a + b + c + d) not in known_metre_patterns
    known_metre_patterns[a + b + c + d] = match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.FULL, issues)
  for (a, b) in itertools.product(patterns_odd, patterns_even):
    assert a + b not in known_partial_patterns
    known_partial_patterns[a + b] = [match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.HALF, issues)]
  for a in patterns_odd:
    issues = [match_result.ISSUES.PADANTA_LAGHU] if a.endswith('L') else []
    assert a not in known_partial_patterns
    known_partial_patterns[a] = [match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.ODD_PADA, issues)]
  for a in patterns_even:
    issues = [match_result.ISSUES.PADANTA_LAGHU] if a.endswith('L') else []
    assert a not in known_partial_patterns
    known_partial_patterns[a] = [match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.EVEN_PADA, issues)]


def AddVishamavrttaPattern(metre_name, line_patterns):
  """Given the four lines of a viṣama-vṛtta, add the metre."""
  assert len(line_patterns) == 4
  line_patterns = [CleanUpPattern(p) for p in line_patterns]
  for p in line_patterns:
    assert re.match(r'^[LG]*$', p)
  (pa, pb, pc, pd) = line_patterns
  assert pb.endswith('G')
  assert pd.endswith('G')
  patterns_a = [pa]
  patterns_b = [pb[:-1] + 'G', pb[:-1] + 'L']
  patterns_c = [pc]
  patterns_d = [pd[:-1] + 'G', pd[:-1] + 'L']
  for (a, b, c, d) in itertools.product(patterns_a, patterns_b,
                                        patterns_c, patterns_d):
    assert (a + b + c + d) not in known_metre_patterns
    known_metre_patterns[a + b + c + d] = match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.FULL, [])
  for (a, b) in itertools.product(patterns_a, patterns_b):
    assert a + b not in known_metre_patterns
    known_partial_patterns[a + b] = [match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.FIRST_HALF, [])]
  for (c, d) in itertools.product(patterns_c, patterns_d):
    assert c + d not in known_partial_patterns
    known_partial_patterns[c + d] = [match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.SECOND_HALF, [])]


def AddMetreRegex(metre_name, line_regexes, issues=None, simple=True):
  """Given regexes for the four lines of a metre, add it."""
  assert len(line_regexes) == 4, (metre_name, line_regexes)
  if simple:
    line_regexes = [CleanUpSimpleRegex(s) for s in line_regexes]
  full_verse_regex = ''.join('(%s)' % s for s in line_regexes)
  match = match_result.MatchResult(metre_name, match_result.MATCH_TYPE.FULL,
                                   issues)
  known_metre_regexes.append((re.compile('^' + full_verse_regex + '$'), match))


def AddSamavrttaRegex(metre_name, line_regex):
  """Add a sama-vṛtta's regex (full, half, pāda). No variants."""
  line_regex = CleanUpSimpleRegex(line_regex)
  full_verse_regex = ''.join('(%s)' % s for s in [line_regex] * 4)
  match = match_result.MatchResult(metre_name, match_result.MATCH_TYPE.FULL, [])
  known_metre_regexes.append((re.compile('^' + full_verse_regex + '$'), match))
  half_verse_regex = ''.join('(%s)' % s for s in [line_regex] * 2)
  match = match_result.MatchResult(metre_name, match_result.MATCH_TYPE.HALF, [])
  known_partial_regexes.append((re.compile('^' + half_verse_regex + '$'),
                                match))
  match = match_result.MatchResult(metre_name, match_result.MATCH_TYPE.PADA, [])
  known_partial_regexes.append((re.compile('^' + line_regex + '$'), match))


def AddAnustup():
  """Add Anuṣṭup to the list of regexes."""
  regex_ac = '....LGG.'
  regex_bd = '....LGL.'
  half_regex = regex_ac + regex_bd
  full_regex = half_regex * 2

  match = match_result.MatchResult('Anuṣṭup (Śloka)',
                                   match_result.MATCH_TYPE.FULL,
                                   [])
  known_metre_regexes.append((re.compile('^' + full_regex + '$'), match))

  match = match_result.MatchResult('Anuṣṭup (Śloka)',
                                   match_result.MATCH_TYPE.HALF,
                                   [])
  known_partial_regexes.append((re.compile('^' + half_regex + '$'), match))

  match = match_result.MatchResult('Anuṣṭup (Śloka)',
                                   match_result.MATCH_TYPE.ODD_PADA,
                                   [])
  known_partial_regexes.append((re.compile('^' + regex_ac + '$'), match))

  match = match_result.MatchResult('Anuṣṭup (Śloka)',
                                   match_result.MATCH_TYPE.EVEN_PADA,
                                   [])
  known_partial_regexes.append((re.compile('^' + regex_bd + '$'), match))


def AddAnustupExamples():
  """Examples of variation from standard Anuṣṭup."""
  # "jayanti te sukṛtino..."
  AddMetreRegex('Anuṣṭup (Śloka)',
                ['LGLGLLLG', '....LGL.', '....LGG.', '....LGL.'],
                [match_result.ISSUES.FIRST_PADA_OFF])
  # "sati pradīpe saty agnau..." Proof: K48.130 (p. 51)
  AddMetreRegex('Anuṣṭup (Śloka)',
                ['LGLGGGGG', '....LGL.', '....LGG.', '....LGL.'],
                [match_result.ISSUES.FIRST_PADA_OFF])
  # "guruṇā stana-bhāreṇa [...] śanaiś-carābhyāṃ pādābhyāṃ" K48.132 (52)
  AddMetreRegex('Anuṣṭup (Śloka)',
                ['....LGG.', '....LGL.', 'LGLGGGGG', '....LGL.'],
                [match_result.ISSUES.THIRD_PADA_OFF])
  # "tāvad evāmṛtamayī..." K48.125 (49)
  AddMetreRegex('Anuṣṭup (Śloka)',
                ['GLGGLLLG', '....LGL.', '....LGG.', '....LGL.'],
                [match_result.ISSUES.FIRST_PADA_OFF])
  # Covers a lot of cases
  AddMetreRegex('Anuṣṭup (Śloka)',
                ['........', '....LGL.', '....LGG.', '....LGL.'],
                [match_result.ISSUES.FIRST_PADA_OFF])
  AddMetreRegex('Anuṣṭup (Śloka)',
                ['....LGG.', '....LGL.', '........', '....LGL.'],
                [match_result.ISSUES.THIRD_PADA_OFF])
  AddMetreRegex('Anuṣṭup (Śloka)',
                ['........', '....LGL.', '........', '....LGL.'],
                [match_result.ISSUES.FIRST_PADA_OFF,
                 match_result.ISSUES.THIRD_PADA_OFF])


def MatraCount(pattern):
  assert re.match('^[LG]*$', pattern)
  return sum(2 if c == 'G' else 1 for c in pattern)


def AddArya(line_patterns):
  """Add an example of Arya, with proper morae checking."""
  assert len(line_patterns) == 4
  expected = [12, 18, 12, 15]
  for i in range(4):
    allow_loose_ending = False
    if i % 2 and line_patterns[i].endswith('L'):
      allow_loose_ending = True
      expected[i] -= 1
    assert MatraCount(line_patterns[i]) == expected[i]
    if allow_loose_ending:
      line_patterns[i] = line_patterns[i][:-1] + '.'
  # TODO(shreevatsa): Should we just add (up to) 4 patterns instead?
  AddMetreRegex('Āryā', line_patterns, simple=False)


def AddAryaExamples():
  """Add collected examples of the Āryā metre."""
  # From Bhartṛhari (BharSt_1.3, ajñaḥ sukham ārādhyaḥ...)
  AddArya(['GGLLGGG', 'LLLLGGLGLGGG', 'GLLLGLGG', 'GGLLGLGLLL'])
  # From Bhartṛhari (BharSt_1.37, siṃhaḥ śiśur api nipatati...)
  AddArya(['GGLLLLLLLL', 'LLLLLLGLGLLLGG', 'LLLLGGLLG', 'LLLLGGLGGL'])
  # From Bhartṛhari (BharSt_1.43, dānaṃ bhogo nāśas...)
  AddArya(['GGGGGG', 'GGLLGLGLGGL', 'GLLGLLGG', 'GLLGGLGLLL'])
  # From Bhartṛhari (BharSt_1.61, mṛga-mīna-sajjanānāṃ...)
  AddArya(['LLGLGLGG', 'LLLLGGLLLLGGG', 'GLLGLLLLG', 'GGLLGLGLLL'])
  # From Bhartṛhari (BharSt_1.87, chinno 'pi rohati taruḥ...)
  AddArya(['GGLGLLLG', 'GGLLGLGLGGL', 'LLLLGGGG', 'GGGGLGGL'])
  # From Bhartṛhari (BharSt_1.104, apriya-vacana-daridraiḥ...)
  AddArya(['GLLLLLLGG', 'LLLLGGLGLLLGG', 'LLLLGLLGG', 'LGLGGLGLLG'])
  # From Bhartṛhari (BharSt_2.60, "kaś cumbati kula-puruṣo...")
  AddArya(['GGLLLLLLG', 'GGLLGLGLGLLL', 'GLLLGLGLL', 'LLLLGGLLLGL'])
  # From Bhartṛhari ("virahe 'pi saṅgamaḥ khalu...", K48.328 (129))
  AddArya(['LLGLGLGLL', 'LGLGGLGLGGG', 'LLLLLLLLGG', 'LGLLLGLGLLL'])
  # From Bhartṛhari ("sva-para-pratārako...", K48.120 (47))
  AddArya(['LLGLGLGG', 'GLLGGLGLGLLG', 'GGLLGLLG', 'GGGGLGLLL'])
  # From Bhartṛhari ("prathitaḥ praṇayavatīnāṃ...", K48.274 (107))
  AddArya(['LLGLLLLGG', 'GGLLGLGLLLGG', 'LLLLGGGLL', 'LLLLGLLLLLGL'])
  # From Bhartṛhari ("sahakāra-kusuma-kesara-...", K48.340 (132))
  AddArya(['LLGLLLLGLL', 'LLLLGGLGLLLGG', 'LLLLLLLLLLG', 'LGLGGLGGG'])
  # From Bhartṛhari ("upari ghanaṃ...", K48.87 (34))
  AddArya(['LLLLGLLLLG', 'GGLLGLGLLLGG', 'LLLLGLLLLG', 'GGLLGLGLLL'])
  # From Bhartṛhari ("yady asya..", K48.309 (121))
  AddArya(['GGLGLLLG', 'GGGGLGLGGL', 'LLGGLLGG', 'LLGGGLGGG'])


def PatternsOfLength(n):
  if n in patterns_memo:
    return patterns_memo[n]
  patterns_memo[n] = [p + 'L' for p in PatternsOfLength(n - 1)]
  patterns_memo[n] += [p + 'G' for p in PatternsOfLength(n - 2)]
  return patterns_memo[n]
patterns_memo = {0: [''], 1: ['L']}


def AddAryaRegex():
  AddMetreRegex('Āryā (matched from regex)',
                ['|'.join(PatternsOfLength(12)),
                 '|'.join([p + '[LG]' for p in PatternsOfLength(16)]),
                 '|'.join(PatternsOfLength(12)),
                 '|'.join([p + '[LG]' for p in PatternsOfLength(13)])],
                simple=False)


def AddGiti(line_patterns):
  """Add an example of Gīti, with proper morae checking."""
  assert len(line_patterns) == 4
  expected = [12, 18, 12, 18]
  for i in range(4):
    allow_loose_ending = False
    if i % 2 and line_patterns[i].endswith('L'):
      allow_loose_ending = True
      expected[i] -= 1
    assert MatraCount(line_patterns[i]) == expected[i], (
        i, line_patterns[i], MatraCount(line_patterns[i]), expected[i])
    if allow_loose_ending:
      line_patterns[i] = line_patterns[i][:-1] + '.'
  # TODO(shreevatsa): Should we just add (up to) 4 patterns instead?
  AddMetreRegex('Gīti', line_patterns, simple=False)


def AddGitiExamples():
  # From Bhartṛhari (BharSt_2.26, āmīlitanayanānāṃ...)
  AddGiti(['GGLLLLGG', 'GLLLLGLGLGGL', 'LLGLGLGLL', 'LLLLLLGLGLGLLL'])
  # The version of the above in Kosambi
  AddGiti(['GGLLLLGG', 'GLLLLGLGLGLLG', 'LLGLGLGLL', 'GLLLLGLGLGLLG'])


def AddKarambajati():
  """Examples of Upajāti of Vaṃśastham and Indravaṃśā."""
  # # Bhartṛhari
  # AddSamavrttaPattern('Vaṃśastham (Vaṃśasthavila)', 'L G L G G L L G L G L G')
  # # Māgha
  # AddSamavrttaPattern('Indravaṃśā', 'G G L G G L L G L G L G')
  # Also add all their Upajāti mixtures, with the above two 0000 and 1111
  # Allow final laghu
  # AddSamavrttaRegex('Karambajāti (Vaṃśastham/Indravaṃśā)',
  #                   '. G L G G L L G L G L .')
  AddSamavrttaRegex('Vaṃśastham/Indravaṃśā',
                    '. G L G G L L G L G L .')
  # # 0001
  # AddExactVrtta('Śīlāturā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['LGLGGLLGLGLG',
  #                'LGLGGLLGLGLG',
  #                'LGLGGLLGLGLG',
  #                'GGLGGLLGLGLG'])
  # # 0010
  # AddExactVrtta('Vaidhātrī (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['L G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G'])
  # # 0011
  # AddExactVrtta('Indumā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['L G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G'])
  # # 0100
  # AddExactVrtta('Ramaṇā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'L G L G G L L G L G L G'])
  # # 0101
  # AddExactVrtta('Upameyā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G'] * 2)
  # # 0110
  # AddExactVrtta('Manahāsā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G'])
  # # 0111
  # AddExactVrtta('Varāsikā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G'])
  # # 1000
  # AddExactVrtta('Kumārī (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'L G L G G L L G L G L G'])
  # # 1001
  # AddExactVrtta('Saurabheyī (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G'])
  # # 1010
  # AddExactVrtta('Śiśirā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G'] * 2)
  # # 1011
  # AddExactVrtta('Ratākhyānakī (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G'])
  # # 1100
  # AddExactVrtta('Śaṅkhacūḍā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'L G L G G L L G L G L G'])
  # # 1101
  # AddExactVrtta('Puṣṭidā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G'])
  # # 1110
  # AddExactVrtta('Vāsantikā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G'])


def InitializeData():
  """Add all known metres to the data structures."""
  AddAnustup()
  AddAnustupExamples()

  # AddMatravrtta('Āryā (mātrā)', [12, 18, 12, 15])
  AddAryaExamples()
  AddAryaRegex()
  AddGitiExamples()

  # Bhartṛhari
  # viṣama-pādānta-laghu is VERY common, so leave last syllable free.
  AddSamavrttaRegex('Upajāti', '. G L G G L L G L G .')

  AddKarambajati()

  # Bhartṛhari
  AddSamavrttaPattern('Rathoddhatā', 'G L G L L L G L G L G')
  # Bhāravi
  AddSamavrttaPattern('Svāgatā', 'G L G L L L G L L G G')
  # Bhartṛhari
  AddSamavrttaPattern('Drutavilambitam', 'L L L G L L G L L G L G')
  # Māgha
  AddSamavrttaPattern('Mañjubhāṣiṇī', 'L L G L G L L L G L G L G')
  # Bhartṛhari
  AddSamavrttaPattern('Śālinī', 'G G G G — G L G G L G G')
  # Bhāravi
  AddSamavrttaPattern('Praharṣiṇī', 'G G G L L L L G L G L G G')
  # AddSamavrttaPattern('Bhujañgaprayātam', 'L G G L G G L G G L G G')
  # AddSamavrttaPattern('Toṭakam', 'L L G L L G L L G L L G')
  # AddSamavrttaPattern('Sragviṇī', 'G L G G L G G L G G L G')
  # Bhāravi
  AddSamavrttaPattern('Pramitākṣarā', 'L L G L G L L L G L L G')
  # Bhartṛhari
  AddSamavrttaPattern('Vasantatilakā', 'G G L G L L L G L L G L G G')
  # Bhartṛhari
  AddSamavrttaPattern('Mālinī', 'L L L L L L G G — G L G G L G G')
  # AddSamavrttaPattern('Cārucāmaram', 'G L G L G L G L G L G L G L G')
  # AddSamavrttaPattern('Pañcacāmaram', 'L G L G L G L G L G L G L G L G')
  # Meghadūta
  AddSamavrttaPattern('Mandākrāntā', 'G G G G — L L L L L G — G L G G L G G')
  # Bhartṛhari
  AddSamavrttaPattern('Śikhariṇī', 'L G G G G G – L L L L L G G — L L L G')
  # Bhartṛhari
  AddSamavrttaPattern('Hariṇī', 'L L L L L G — G G G G — L G L L G L G')
  # Bhartṛhari
  AddSamavrttaPattern('Pṛthvī', 'L G L L L G L G—L L L G L G G L G')
  # AddSamavrttaPattern('Kokilalam (Nardaṭakam)',
  #              'L L L L G L G L L L G — L L G L L G')
  # AddSamavrttaPattern('Mallikāmālā (Matta-kokilā)',
  #              'G L G L L G L G L L G L G L L G L G')
  # Bhartṛhari
  AddSamavrttaPattern('Śārdūlavikrīḍitam',
                      'G G G L L G L G L L L G — G G L G G L G')
  # Bhartṛhari
  AddSamavrttaPattern('Sragdharā',
                      'G G G G L G G — L L L L L L G — G L G G L G G')
  # Bhartṛhari
  AddArdhasamavrttaPattern('Viyoginī',
                           'L L G   L L G L G L G',
                           'L L G G L L G L G L G')
  # Bhāravi
  AddArdhasamavrttaPattern('Aupacchandasikam (Vasantamālikā) (Upodgatā)',
                           'L L G   L L G L G L G G',
                           'L L G G L L G L G L G G')
  # Bhāravi
  AddArdhasamavrttaPattern('Aparavaktrā',
                           'L L L L L L G — L G L G',
                           'L L L L G — L L G L G L G')
  # Bhartṛhari
  AddArdhasamavrttaPattern('Puṣpitāgrā',
                           'L L L L L L G L G L G G',
                           'L L L L G L L G L G L G G')
  # Bhāravi
  AddVishamavrttaPattern('Udgatā', ['L L  G  L  G  L L L G L',
                                    'L L L L L  G  L  G  L G',
                                    ' G  L L L L L L  G  L L G',
                                    'L L  G  L  G  L L L  G  L G L G'])
  # AddSamavrttaPattern('Aśvadhāṭī (Sitastavaka?)',
  #              'G G L G L L L – G G L G L L L – G G L G L L L G')
  # AddSamavrttaPattern('Śivatāṇḍava',
  #              'L G L L  L G L L  L G L L  L G L L  L G L L  L G L L  L G')
  # Bhartṛhari
  AddSamavrttaPattern('Dodhakam', 'G L L G L L G L L G G')
  # # AddMatravrtta('Pādākulakam (and many other names)', ['4 * 4'] * 4)
  # AddSamavrttaPattern('Mālatī', 'L L L L G L L G L G L G')
  # AddSamavrttaPattern('Madīrā',
  #                     'G L L  G L L  G L L  G L L  G L L  G L L  G L L  G')
  # Bhāravi
  AddSamavrttaPattern('Matta-mayūram', 'G G G G – G L L G G – L L G G')
  # AddSamavrttaPattern('Vidyunmālā', 'G G G G G G G G')

  # Bhāravi
  AddSamavrttaPattern('Kṣamā (Candrikā, Utpalinī)', 'LLLLLLGGLGGLG')

  # Bhāravi
  AddSamavrttaPattern('Prabhā (Mandākinī)', 'LLLLLLGLGGLG')

  # Bhāravi
  AddSamavrttaPattern('Jaladharamālā', 'GGGGLLLLGGGG')
  # Bhāravi
  AddSamavrttaPattern('Jaloddhatagatiḥ', 'LGLLLGLGLLLG')

  # Bhāravi
  AddSamavrttaPattern('Madhyakṣāmā (Haṃsaśyenī, Kuṭila, Cūḍāpīḍam)',
                      'G G G G L L L L L L G G G G')

  # Bhāravi
  AddSamavrttaPattern('Vaṃśapatrapatitam (Vaṃśadala)',
                      'G L L G L G L L L G L L L L L L G')

  # Māgha
  AddSamavrttaPattern('Rucirā (Prabhāvatī)', 'L G L G L L L L G L G L G')

  # Raghuvamśa (hard to believe, but there it is)
  AddSamavrttaPattern('Nārācam', 'L L L L L L G L G G L G G L G G L G')
