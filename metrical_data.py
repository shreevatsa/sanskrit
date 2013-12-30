#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Data structures that store matching metres for known patterns."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import logging
import re

import simple_utils


class AllMetricalData(object):
  """Known patterns and regexes, both full and partial."""

  def __init__(self, known_metre_patterns, known_metre_regexes,
               known_partial_patterns):
    self.known_metre_patterns = known_metre_patterns
    self.known_metre_regexes = known_metre_regexes
    self.known_partial_patterns = known_partial_patterns


# Poor man's enum for now. Python adds enum support in Python 3.4+.
def Enum(**enums):
  return type(str('Enum'), (), enums)

ISSUES = Enum(UNKNOWN_ISSUE=0,
              VISAMA_PADANTA_LAGHU='viṣama-pādānta-laghu',
              PADANTA_LAGHU='pādānta-laghu',
              FIRST_PADA_OFF='first pāda not conforming',
              THIRD_PADA_OFF='third pāda not conforming'
             )

MATCH_TYPE = Enum(UNKNOWN=0,
                  FULL=1,
                  PADA=2,
                  ODD_PADA=3,
                  EVEN_PADA=4,
                  HALF=5,
                  FIRST_HALF=6,
                  SECOND_HALF=7,
                  PADA_1=8,
                  PADA_2=9,
                  PADA_3=10,
                  PADA_4=11
                 )


class MatchResult(object):
  """Result of match against some known pattern/regex: metre with some info."""

  def __init__(self, metre_name, match_type, issues=None):
    self.metre_name = metre_name
    self.match_type = match_type
    if issues is None:
      self.issues = []
    else:
      assert isinstance(issues, list)
      self.issues = issues

  def __str__(self):
    return self.Name()

  def NameWithMatchType(self):
    assert self.match_type
    return {
        MATCH_TYPE.FULL: '%s',
        MATCH_TYPE.HALF: 'Half of %s',
        MATCH_TYPE.PADA: 'One pāda of %s',
        MATCH_TYPE.ODD_PADA: 'Odd pāda of %s',
        MATCH_TYPE.EVEN_PADA: 'Even pāda of %s',
        MATCH_TYPE.FIRST_HALF: 'First half of %s',
        MATCH_TYPE.SECOND_HALF: 'Second half of %s',
        MATCH_TYPE.PADA_1: 'First pāda of %s',
        MATCH_TYPE.PADA_2: 'Second pāda of %s',
        MATCH_TYPE.PADA_3: 'Third pāda of %s',
        MATCH_TYPE.PADA_4: 'Fourth pāda of %s'
        }[self.match_type] % self.metre_name

  def Name(self):
    """Name of the match, including match type and issues."""
    name = self.NameWithMatchType()
    if self.issues:
      return name + ' (with %s)' % ', '.join(self.issues)
    else:
      return name

  def MetreName(self):
    if self.issues:
      return self.metre_name + ' (with %s)' % ', '.join(self.issues)
    else:
      return self.metre_name

  def MetreNameOnlyBase(self):
    return self.metre_name


known_patterns = {}
known_metres = {}
# known_morae = {}


# Unless we want to create another type for a list of MatchResults
def Names(match_results):
  return ' AND '.join(m.Name() for m in match_results)


def Description(match_results, indent_depth=0):
  indent = ' ' * indent_depth
  s = ''
  for (i, result) in enumerate(match_results):
    s += indent + 'Result %d: ' % i
    s += '\n' + indent + '\tMetre name: %s' % result.metre_name
    s += '\n' + indent + '\tMatch type: %s' % result.match_type
    s += '\n' + indent + '\tIssues: %s' % result.issues
  return s


def CleanUpPatternString(pattern):
  pattern = simple_utils.RemoveChars(pattern, ' —–')
  chars = ['L', 'G', '.', '(', ')', '[', r'\]', '|']
  assert re.match(r'^[%s]*$' % ''.join(chars), pattern), pattern
  return pattern


def LaghuEnding(pattern):
  assert re.match(r'^[LG.]*$', pattern)
  assert pattern.endswith('.') or pattern.endswith('G'), pattern
  return pattern[:-1] + 'L'


def LooseEnding(pattern):
  assert re.match(r'^[LG.]*$', pattern)
  assert pattern.endswith('.') or pattern.endswith('G'), pattern
  return pattern[:-1] + '.'


def OptionsExpand(pattern):
  """Given pattern with n '.'s, yields all 2^n patterns with L and G only."""
  where = pattern.find('.')
  if where == -1:
    yield pattern
    return
  prefix = pattern[:where]
  for suffix in OptionsExpand(pattern[where + 1:]):
    for fix in ['L', 'G']:
      yield prefix + fix + suffix


def AddPadaWithFinalLaghu(metre_name, pattern, match_type=MATCH_TYPE.PADA):
  assert re.match(r'^[LG]*L$', pattern)
  if pattern in known_patterns:
    logging.warning('Not adding %s for %s. It is already known as %s', pattern,
                    metre_name, Names(known_patterns[pattern]))
  else:
    known_patterns[pattern] = [MatchResult(metre_name, match_type,
                                           [ISSUES.PADANTA_LAGHU])]


def AddPada(metre_name, pattern, match_type=MATCH_TYPE.PADA):
  assert re.match(r'^[LG]*$', pattern)
  if pattern in known_patterns:
    logging.warning('Pattern %s, being added for %s, is already known as %s',
                    pattern, metre_name, Names(known_patterns[pattern]))

    known_patterns[pattern].append(MatchResult(metre_name, match_type))
  else:
    known_patterns[pattern] = [MatchResult(metre_name, match_type)]
  if pattern.endswith('G'):
    AddPadaWithFinalLaghu(metre_name, LaghuEnding(pattern), match_type)


def AddArdha(metre_name, pattern_odd, pattern_even,
             match_type=MATCH_TYPE.HALF):
  """Given the patterns of odd and even pādas, add to the data structures."""
  assert re.match(r'^[LG.]*$', pattern_odd)
  assert re.match(r'^[LG.]*$', pattern_even)
  assert pattern_even.endswith('.')
  odds = OptionsExpand(pattern_odd)
  # Making this a list as we use it twice.
  evens = list(OptionsExpand(pattern_even))
  for (o, e) in itertools.product(odds, evens):
    known_patterns[o + e] = known_patterns.get(o + e, [])
    known_patterns[o + e].append(MatchResult(metre_name, match_type))
  # Also add the viṣama-pādānta-laghu variants
  if pattern_odd.endswith('G'):
    odds = OptionsExpand(LaghuEnding(pattern_odd))
    for (o, e) in itertools.product(odds, evens):
      known_patterns[o + e] = known_patterns.get(o + e, [])
      known_patterns[o + e].append(
          MatchResult(metre_name, match_type, [ISSUES.VISAMA_PADANTA_LAGHU]))


def AddVrtta(metre_name, verse_pattern, issues=None):
  assert verse_pattern not in known_metres, (verse_pattern,
                                             known_metres[verse_pattern])
  logging.debug('Adding metre %s with pattern %s', metre_name, verse_pattern)
  known_metres[verse_pattern] = MatchResult(metre_name, MATCH_TYPE.FULL,
                                            issues)


def AddVrttaWithVPL(metre_name, verse_pattern):
  assert verse_pattern not in known_metres, (verse_pattern,
                                             known_metres[verse_pattern])
  logging.debug('Adding viṣama-pādānta-laghu variant of metre %s '
                'with pattern %s', metre_name, verse_pattern)
  known_metres[verse_pattern] = MatchResult(
      metre_name, MATCH_TYPE.FULL, [ISSUES.VISAMA_PADANTA_LAGHU])


def AddExactVrtta(metre_name, line_patterns, issues=None):
  """Given the four lines of a vṛtta, add it to the data structures exactly."""
  assert len(line_patterns) == 4, (metre_name, line_patterns)
  AddVrtta(metre_name, CleanUpPatternString(''.join(line_patterns)), issues)


def AddFourLineVrtta(metre_name, line_patterns):
  """Given the four lines of a vṛtta, add it to the data structures."""
  assert len(line_patterns) == 4, (metre_name, line_patterns)
  clean = [CleanUpPatternString(pattern) for pattern in line_patterns]
  for pattern in clean:
    assert re.match(r'^[LG.]*$', pattern)
  loose = [None, LooseEnding(clean[1]), None, LooseEnding(clean[3])]
  assert clean[1].endswith('G')
  assert clean[3].endswith('G')
  full_verse_pattern = clean[0] + loose[1] + clean[2] + loose[3]
  AddVrtta(metre_name, full_verse_pattern)
  # Now add the other variations as well
  tolerable = []
  if clean[2].endswith('G'):
    tolerable.append(clean[0] + loose[1] + LaghuEnding(clean[2]) + loose[3])
  if clean[0].endswith('G'):
    laghu0 = LaghuEnding(clean[0])
    tolerable.append(laghu0 + loose[1] + clean[2] + loose[3])
    if clean[2].endswith('G'):
      tolerable.append(laghu0 + loose[1] + LaghuEnding(clean[2]) + loose[3])
  for verse_pattern in tolerable:
    AddVrttaWithVPL(metre_name, verse_pattern)


def AddSamavrtta(metre_name, each_line_pattern):
  """Given a sama-vṛtta metre, add it to the data structures."""
  clean = CleanUpPatternString(each_line_pattern)
  assert re.match(r'^[LG.]*$', clean)
  assert clean.endswith('G'), (clean, metre_name)
  loose = LooseEnding(clean)
  AddFourLineVrtta(metre_name, [clean] * 4)
  AddArdha(metre_name, clean, loose)
  for explicit_pattern in OptionsExpand(clean):
    AddPada(metre_name, explicit_pattern)


def AddArdhasamavrtta(metre_name, odd_line_pattern, even_line_pattern):
  """Given an ardha-sama-vṛtta metre, add it to the data structures."""
  clean_odd = CleanUpPatternString(odd_line_pattern)
  assert re.match(r'^[LG.]*$', clean_odd)
  clean_even = CleanUpPatternString(even_line_pattern)
  assert re.match(r'^[LG.]*$', clean_even)

  AddFourLineVrtta(metre_name, [clean_odd, clean_even] * 2)
  AddArdha(metre_name, clean_odd, LooseEnding(clean_even))
  for explicit_pattern in OptionsExpand(clean_odd):
    AddPada(metre_name, explicit_pattern, MATCH_TYPE.ODD_PADA)
  for explicit_pattern in OptionsExpand(clean_even):
    AddPada(metre_name, explicit_pattern, MATCH_TYPE.EVEN_PADA)


def AddVishamavrtta(metre_name, line_patterns):
  """Given a viṣama-vṛtta metre, add it to the data structures."""
  AddFourLineVrtta(metre_name, line_patterns)
  clean = [CleanUpPatternString(pattern) for pattern in line_patterns]
  AddArdha(metre_name, clean[0], LooseEnding(clean[1]), MATCH_TYPE.FIRST_HALF)
  AddArdha(metre_name, clean[2], LooseEnding(clean[3]),
           MATCH_TYPE.SECOND_HALF)
  for (i, line) in enumerate(line_patterns):
    line = CleanUpPatternString(line)
    assert re.match(r'^[LG.]*$', line)
    for pattern in OptionsExpand(line):
      AddPada(metre_name, pattern, getattr(MATCH_TYPE, 'PADA_%d' % (i + 1)))


# def AddMatravrtta(metre_name, line_morae):
#   known_morae[repr(line_morae)] = metre_name
#   if len(line_morae) == 4:
#     # Not ideal (lossy), but input is often like this.
#     known_morae[repr([line_morae[0] + line_morae[1],
#                       line_morae[2] + line_morae[3]])] = metre_name


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
    assert MatraCount(line_patterns[i]) == expected[i], (
        line_patterns[i], MatraCount(line_patterns[i]))
    if allow_loose_ending:
      line_patterns[i] = line_patterns[i][:-1] + '.'
  AddExactVrtta('Āryā', line_patterns)


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
  # # From Bhartṛhari ("upari ghanaṃ...", K48.87 (34))
  # AddArya(['LLLLGLLLLG', 'GGLLGLGLLLGG', 'LLLLGLLLLG', 'GGLLGLGLLL'])
  # From Bhartṛhari ("yady asya..", K48.309 (121))
  AddArya(['GGLGLLLG', 'GGGGLGLGGL', 'LLGGLLGG', 'LLGGGLGGG'])


def AddGitiExamples():
  # From Bhartṛhari (BharSt_2.26, āmīlitanayanānāṃ...)
  AddExactVrtta('Gīti',
                ['GGLLLLGG', 'GLLLLGLGLGGL', 'LLGLGLGLL', 'LLLLLLGLGLGGLL'])
  # The version of the above in Kosambi
  AddExactVrtta('Gīti',
                ['GGLLLLGG', 'GLLLLGLGLGLLG', 'LLGLGLGLL', 'GLLLLGLGLGLLG'])


def AddAnustupExamples():
  """Examples of variation from standard Anuṣṭup."""
  # "jayanti te sukṛtino..."
  AddExactVrtta('Anuṣṭup (Śloka)',
                ['LGLGLLLG', '....LGL.', '....LGG.', '....LGL.'],
                [ISSUES.FIRST_PADA_OFF])
  # "sati pradīpe saty agnau..." Proof: K48.130 (p. 51)
  AddExactVrtta('Anuṣṭup (Śloka)',
                ['LGLGGGGG', '....LGL.', '....LGG.', '....LGL.'],
                [ISSUES.FIRST_PADA_OFF])
  # "guruṇā stana-bhāreṇa [...] śanaiś-carābhyāṃ pādābhyāṃ" K48.132 (52)
  AddExactVrtta('Anuṣṭup (Śloka)',
                ['....LGG.', '....LGL.', 'LGLGGGGG', '....LGL.'],
                [ISSUES.THIRD_PADA_OFF])
  # "tāvad evāmṛtamayī..." K48.125 (49)
  AddExactVrtta('Anuṣṭup (Śloka)',
                ['GLGGLLLG', '....LGL.', '....LGG.', '....LGL.'],
                [ISSUES.FIRST_PADA_OFF])
  # Covers a lot of cases
  AddExactVrtta('Anuṣṭup (Śloka)',
                ['........', '....LGL.', '....LGG.', '....LGL.'],
                [ISSUES.FIRST_PADA_OFF])
  AddExactVrtta('Anuṣṭup (Śloka)',
                ['....LGG.', '....LGL.', '........', '....LGL.'],
                [ISSUES.THIRD_PADA_OFF])
  AddExactVrtta('Anuṣṭup (Śloka)',
                ['........', '....LGL.', '........', '....LGL.'],
                [ISSUES.FIRST_PADA_OFF,
                 ISSUES.THIRD_PADA_OFF])


def AddLongerUpajati():
  """Examples of Upajāti of Vaṃśastham and Indravaṃśā."""
  # Bhartṛhari
  AddSamavrtta('Vaṃśastham (Vaṃśasthavila)', 'L G L G G L L G L G L G')
  # Māgha
  AddSamavrtta('Indravaṃśā', 'G G L G G L L G L G L G')
  # Also add all their Upajāti mixtures, with the above two 0000 and 1111
  # AddSamavrtta('Upajāti of Vaṃśastham and Indravaṃśā',
  #              '. G L G G L L G L G L G')
  # 0001
  AddExactVrtta('Śīlāturā (Upajāti of Vaṃśastham and Indravaṃśā)',
                ['LGLGGLLGLGLG',
                 'LGLGGLLGLGLG',
                 'LGLGGLLGLGLG',
                 'GGLGGLLGLGLG'])
  # 0010
  AddExactVrtta('Vaidhātrī (Upajāti of Vaṃśastham and Indravaṃśā)',
                ['L G L G G L L G L G L G',
                 'L G L G G L L G L G L G',
                 'G G L G G L L G L G L G',
                 'L G L G G L L G L G L G'])
  # 0011
  AddExactVrtta('Indumā (Upajāti of Vaṃśastham and Indravaṃśā)',
                ['L G L G G L L G L G L G',
                 'L G L G G L L G L G L G',
                 'G G L G G L L G L G L G',
                 'G G L G G L L G L G L G'])
  # 0100
  AddExactVrtta('Ramaṇā (Upajāti of Vaṃśastham and Indravaṃśā)',
                ['L G L G G L L G L G L G',
                 'G G L G G L L G L G L G',
                 'L G L G G L L G L G L G',
                 'L G L G G L L G L G L G'])
  # 0101
  AddExactVrtta('Upameyā (Upajāti of Vaṃśastham and Indravaṃśā)',
                ['L G L G G L L G L G L G',
                 'G G L G G L L G L G L G'] * 2)
  # 0110
  AddExactVrtta('Manahāsā (Upajāti of Vaṃśastham and Indravaṃśā)',
                ['L G L G G L L G L G L G',
                 'G G L G G L L G L G L G',
                 'G G L G G L L G L G L G',
                 'L G L G G L L G L G L G'])
  # 0111
  AddExactVrtta('Varāsikā (Upajāti of Vaṃśastham and Indravaṃśā)',
                ['L G L G G L L G L G L G',
                 'G G L G G L L G L G L G',
                 'G G L G G L L G L G L G',
                 'G G L G G L L G L G L G'])
  # 1000
  AddExactVrtta('Kumārī (Upajāti of Vaṃśastham and Indravaṃśā)',
                ['G G L G G L L G L G L G',
                 'L G L G G L L G L G L G',
                 'L G L G G L L G L G L G',
                 'L G L G G L L G L G L G'])
  # 1001
  AddExactVrtta('Saurabheyī (Upajāti of Vaṃśastham and Indravaṃśā)',
                ['G G L G G L L G L G L G',
                 'L G L G G L L G L G L G',
                 'L G L G G L L G L G L G',
                 'G G L G G L L G L G L G'])
  # 1010
  AddExactVrtta('Śiśirā (Upajāti of Vaṃśastham and Indravaṃśā)',
                ['G G L G G L L G L G L G',
                 'L G L G G L L G L G L G'] * 2)
  # 1011
  AddExactVrtta('Ratākhyānakī (Upajāti of Vaṃśastham and Indravaṃśā)',
                ['G G L G G L L G L G L G',
                 'L G L G G L L G L G L G',
                 'G G L G G L L G L G L G',
                 'G G L G G L L G L G L G'])
  # 1100
  AddExactVrtta('Śaṅkhacūḍā (Upajāti of Vaṃśastham and Indravaṃśā)',
                ['G G L G G L L G L G L G',
                 'G G L G G L L G L G L G',
                 'L G L G G L L G L G L G',
                 'L G L G G L L G L G L G'])
  # 1101
  AddExactVrtta('Puṣṭidā (Upajāti of Vaṃśastham and Indravaṃśā)',
                ['G G L G G L L G L G L G',
                 'G G L G G L L G L G L G',
                 'L G L G G L L G L G L G',
                 'G G L G G L L G L G L G'])
  # 1110
  AddExactVrtta('Vāsantikā (Upajāti of Vaṃśastham and Indravaṃśā)',
                ['G G L G G L L G L G L G',
                 'G G L G G L L G L G L G',
                 'G G L G G L L G L G L G',
                 'L G L G G L L G L G L G'])


def AddAryaRegex():
  four_any = '(LLLL|LLG|LGL|GLL|GG)'
  AddExactVrtta('Āryā (matched from regex)',
                [four_any + four_any + four_any,  # 12 in groups of 4
                 four_any + four_any + four_any + four_any + '[LG]',
                 four_any + four_any + four_any,
                 four_any + four_any + four_any + 'L' + '[LG]'])


def InitializeData():
  """Add all known metres to the data structures."""
  AddArdhasamavrtta('Anuṣṭup (Śloka)', '. . . . L G G G', '. . . . L G L G')
  AddAnustupExamples()

  # AddMatravrtta('Āryā (mātrā)', [12, 18, 12, 15])
  AddAryaExamples()
  AddAryaRegex()
  AddGitiExamples()

  # Bhartṛhari
  AddSamavrtta('Upajāti', '. G L G G L L G L G G')

  AddLongerUpajati()

  # Bhartṛhari
  AddSamavrtta('Rathoddhatā', 'G L G L L L G L G L G')
  # Bhāravi
  AddSamavrtta('Svāgatā', 'G L G L L L G L L G G')
  # Bhartṛhari
  AddSamavrtta('Drutavilambitam', 'L L L G L L G L L G L G')
  # Māgha
  AddSamavrtta('Mañjubhāṣiṇī', 'L L G L G L L L G L G L G')
  # Bhartṛhari
  AddSamavrtta('Śālinī', 'G G G G — G L G G L G G')
  # Bhāravi
  AddSamavrtta('Praharṣiṇī', 'G G G L L L L G L G L G G')
  # AddSamavrtta('Bhujañgaprayātam', 'L G G L G G L G G L G G')
  # AddSamavrtta('Toṭakam', 'L L G L L G L L G L L G')
  # AddSamavrtta('Sragviṇī', 'G L G G L G G L G G L G')
  # Bhāravi
  AddSamavrtta('Pramitākṣarā', 'L L G L G L L L G L L G')
  # Bhartṛhari
  AddSamavrtta('Vasantatilakā', 'G G L G L L L G L L G L G G')
  # Bhartṛhari
  AddSamavrtta('Mālinī', 'L L L L L L G G — G L G G L G G')
  # AddSamavrtta('Cārucāmaram', 'G L G L G L G L G L G L G L G')
  # AddSamavrtta('Pañcacāmaram', 'L G L G L G L G L G L G L G L G')
  # Meghadūta
  AddSamavrtta('Mandākrāntā', 'G G G G — L L L L L G — G L G G L G G')
  # Bhartṛhari
  AddSamavrtta('Śikhariṇī', 'L G G G G G – L L L L L G G — L L L G')
  # Bhartṛhari
  AddSamavrtta('Hariṇī', 'L L L L L G — G G G G — L G L L G L G')
  # Bhartṛhari
  AddSamavrtta('Pṛthvī', 'L G L L L G L G—L L L G L G G L G')
  # AddSamavrtta('Kokilalam (Nardaṭakam)',
  #              'L L L L G L G L L L G — L L G L L G')
  # AddSamavrtta('Mallikāmālā (Matta-kokilā)',
  #              'G L G L L G L G L L G L G L L G L G')
  # Bhartṛhari
  AddSamavrtta('Śārdūlavikrīḍitam', 'G G G L L G L G L L L G — G G L G G L G')
  # Bhartṛhari
  AddSamavrtta('Sragdharā', 'G G G G L G G — L L L L L L G — G L G G L G G')
  # Bhartṛhari
  AddArdhasamavrtta('Viyoginī',
                    'L L G   L L G L G L G',
                    'L L G G L L G L G L G')
  # Bhāravi
  AddArdhasamavrtta('Aupacchandasikam (Vasantamālikā) (Upodgatā)',
                    'L L G   L L G L G L G G', 'L L G G L L G L G L G G')
  # Bhāravi
  AddArdhasamavrtta('Aparavaktrā',
                    'L L L L L L G — L G L G', 'L L L L G — L L G L G L G')
  # Bhartṛhari
  AddArdhasamavrtta('Puṣpitāgrā',
                    'L L L L L L G L G L G G', 'L L L L G L L G L G L G G')
  # Bhāravi
  AddVishamavrtta('Udgatā', ['L L  G  L  G  L L L G L',
                             'L L L L L  G  L  G  L G',
                             ' G  L L L L L L  G  L L G',
                             'L L  G  L  G  L L L  G  L G L G'])
  # AddSamavrtta('Aśvadhāṭī (Sitastavaka?)',
  #              'G G L G L L L – G G L G L L L – G G L G L L L G')
  # AddSamavrtta('Śivatāṇḍava',
  #              'L G L L  L G L L  L G L L  L G L L  L G L L  L G L L  L G')
  # Bhartṛhari
  AddSamavrtta('Dodhakam', 'G L L G L L G L L G G')
  # # AddMatravrtta('Pādākulakam (and many other names)', ['4 * 4'] * 4)
  # AddSamavrtta('Mālatī', 'L L L L G L L G L G L G')
  # AddSamavrtta('Madīrā', 'G L L  G L L  G L L  G L L  G L L  G L L  G L L  G')
  # Bhāravi
  AddSamavrtta('Matta-mayūram', 'G G G G – G L L G G – L L G G')
  # AddSamavrtta('Vidyunmālā', 'G G G G G G G G')

  # Bhāravi
  AddSamavrtta('Kṣamā (Candrikā, Utpalinī)', 'LLLLLLGGLGGLG')

  # Bhāravi
  AddSamavrtta('Prabhā (Mandākinī)', 'LLLLLLGLGGLG')

  # Bhāravi
  AddSamavrtta('Jaladharamālā', 'GGGGLLLLGGGG')
  # Bhāravi
  AddSamavrtta('Jaloddhatagatiḥ', 'LGLLLGLGLLLG')

  # Bhāravi
  AddSamavrtta('Madhyakṣāmā (Haṃsaśyenī, Kuṭila, Cūḍāpīḍam)',
               'G G G G L L L L L L G G G G')

  # Bhāravi
  AddSamavrtta('Vaṃśapatrapatitam (Vaṃśadala)',
               'G L L G L G L L L G L L L L L L G')

  # Māgha
  AddSamavrtta('Rucirā (Prabhāvatī)', 'L G L G L L L L G L G L G')

  # Raghuvamśa (hard to believe, but there it is)
  AddSamavrtta('nārācam', 'L L L L L L G L G G L G G L G G L G')
