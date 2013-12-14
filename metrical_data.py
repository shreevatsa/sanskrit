#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Functions that deal with the actual data."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import logging
import re

import simple_utils

known_patterns = {}
known_metres = {}
known_morae = {}


def Enum(**enums):
  return type(str('Enum'), (), enums)

METRE_PATTERN_ISSUES = Enum(UNKNOWN_ISSUE=0,
                            VISAMA_PADANTA_LAGHU='viṣama-pādānta-laghu',
                            PADANTA_LAGHU='pādānta-laghu')


class MetrePattern(object):
  """A metre pattern."""

  FULL = 1
  PADA = 2
  ODD_PADA = 3
  EVEN_PADA = 4
  HALF = 5
  FIRST_HALF = 6
  SECOND_HALF = 7

  def __init__(self, metre_name, match_type, issues=None):
    self.metre_name = metre_name
    self.match_type = match_type
    self.issues = issues
    if issues:
      assert isinstance(issues, list)

  def __str__(self):
    return self.Name()

  def NameWithMatchType(self):
    assert self.match_type
    return {
        self.FULL: '%s',
        self.HALF: 'Half of %s',
        self.PADA: 'One pāda of %s',
        self.ODD_PADA: 'Odd pāda of %s',
        self.EVEN_PADA: 'Even pāda of %s'
        }[self.match_type] % self.metre_name

  def Name(self):
    """Name of the match, including match type and issues."""
    name = self.NameWithMatchType()
    if self.issues:
      return name + ' (with %s)' % self.issues
    else:
      return name

  def MetreName(self):
    if self.issues:
      return self.metre_name + ' (with %s)' % ', '.join(self.issues)
    else:
      return self.metre_name

  def MetreNameOnlyBase(self):
    return self.metre_name


def Names(metre_patterns):
  return ' AND '.join(m.Name() for m in metre_patterns)


def CleanUpPatternString(pattern):
  pattern = simple_utils.RemoveChars(pattern, ' —–')
  assert re.match(r'^[LG.]*$', pattern), pattern
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


def AddPadaWithFinalLaghu(metre_name, pattern, match_type=MetrePattern.PADA):
  assert re.match(r'^[LG]*L$', pattern)
  if pattern in known_patterns:
    logging.warning('Not adding %s for %s. It is already known as %s', pattern,
                    metre_name, Names(known_patterns[pattern]))
  else:
    known_patterns[pattern] = [MetrePattern(
        metre_name, match_type, [METRE_PATTERN_ISSUES.PADANTA_LAGHU])]


def AddPada(metre_name, pattern, match_type=MetrePattern.PADA):
  assert re.match(r'^[LG]*$', pattern)
  if pattern in known_patterns:
    logging.warning('Pattern %s, being added for %s, is already known as %s',
                    pattern, metre_name, Names(known_patterns[pattern]))

    known_patterns[pattern].append(MetrePattern(metre_name, match_type))
  else:
    known_patterns[pattern] = [MetrePattern(metre_name, match_type)]
  if pattern.endswith('G'):
    AddPadaWithFinalLaghu(metre_name, LaghuEnding(pattern), match_type)


def AddArdha(metre_name, pattern_odd, pattern_even,
             match_type=MetrePattern.HALF):
  """Given the patterns of odd and even pādas, add to the data structures."""
  assert re.match(r'^[LG.]*$', pattern_odd)
  assert re.match(r'^[LG.]*$', pattern_even)
  assert pattern_even.endswith('.')
  odds = OptionsExpand(pattern_odd)
  # Making this a list as we use it twice.
  evens = list(OptionsExpand(pattern_even))
  for (o, e) in itertools.product(odds, evens):
    assert (o + e) not in known_patterns
    known_patterns[o + e] = [MetrePattern(metre_name, match_type)]
  # Also add the viṣama-pādānta-laghu variants
  if pattern_odd.endswith('G'):
    odds = OptionsExpand(LaghuEnding(pattern_odd))
    for (o, e) in itertools.product(odds, evens):
      assert (o + e) not in known_patterns
      known_patterns[o + e] = [
          MetrePattern(metre_name, match_type,
                       [METRE_PATTERN_ISSUES.VISAMA_PADANTA_LAGHU])]


def AddVrtta(metre_name, verse_pattern):
  assert verse_pattern not in known_metres, (verse_pattern,
                                             known_metres[verse_pattern])
  logging.debug('Adding metre %s with pattern %s', metre_name, verse_pattern)
  known_metres[verse_pattern] = MetrePattern(metre_name, MetrePattern.FULL)


def AddVrttaWithVPL(metre_name, verse_pattern):
  assert verse_pattern not in known_metres, (verse_pattern,
                                             known_metres[verse_pattern])
  logging.debug('Adding metre %s (with viṣama-pādānta-laghu) with pattern %s',
                metre_name, verse_pattern)
  known_metres[verse_pattern] = MetrePattern(
      metre_name, MetrePattern.FULL,
      [METRE_PATTERN_ISSUES.VISAMA_PADANTA_LAGHU])


def AddExactVrtta(metre_name, line_patterns):
  """Given the four lines of a vṛtta, add it to the data structures exactly."""
  assert len(line_patterns) == 4, (metre_name, line_patterns)
  for pattern in line_patterns:
    assert pattern == CleanUpPatternString(pattern)
  AddVrtta(metre_name, ''.join(line_patterns))


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
    AddPada(metre_name, explicit_pattern, MetrePattern.ODD_PADA)
  for explicit_pattern in OptionsExpand(clean_even):
    AddPada(metre_name, explicit_pattern, MetrePattern.EVEN_PADA)


def AddVishamavrtta(metre_name, line_patterns):
  """Given a viṣama-vṛtta metre, add it to the data structures."""
  AddFourLineVrtta(metre_name, line_patterns)
  clean = [CleanUpPatternString(pattern) for pattern in line_patterns]
  AddArdha(metre_name, clean[0], LooseEnding(clean[1]), MetrePattern.FIRST_HALF)
  AddArdha(metre_name, clean[2], LooseEnding(clean[3]),
           MetrePattern.SECOND_HALF)
  for (i, line) in enumerate(line_patterns):
    line = CleanUpPatternString(line)
    assert re.match(r'^[LG.]*$', line)
    for pattern in OptionsExpand(line):
      AddPada(metre_name + ' (pāda %d)' % (i + 1), pattern)


def AddMatravrtta(metre_name, line_morae):
  known_morae[repr(line_morae)] = metre_name
  if len(line_morae) == 4:
    # Not ideal (lossy), but input is often like this.
    known_morae[repr([line_morae[0] + line_morae[1],
                      line_morae[2] + line_morae[3]])] = metre_name


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
  # From Bhartṛhari ("upari ghanaṃ...", K48.87 (34))
  AddArya(['LLLLGLLLLG', 'GGLLGLGLLLGG', 'LLLLGLLLLG', 'GGLLGLGLLL'])
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
  AddExactVrtta('Anuṣṭup (Śloka) (with first pāda not conforming)',
                ['LGLGLLLG', '....LGL.', '....LGG.', '....LGL.'])
  # "sati pradīpe saty agnau..." Proof: K48.130 (p. 51)
  AddExactVrtta('Anuṣṭup (Śloka) (with first pāda not conforming)',
                ['LGLGGGGG', '....LGL.', '....LGG.', '....LGL.'])
  # "guruṇā stana-bhāreṇa [...] śanaiś-carābhyāṃ pādābhyāṃ" K48.132 (52)
  AddExactVrtta('Anuṣṭup (Śloka) (with third pāda not conforming)',
                ['....LGG.', '....LGL.', 'LGLGGGGG', '....LGL.'])
  # "tāvad evāmṛtamayī..." K48.125 (49)
  AddExactVrtta('Anuṣṭup (Śloka) (with first pāda not conforming)',
                ['GLGGLLLG', '....LGL.', '....LGG.', '....LGL.'])


def InitializeData():
  """Add all known metres to the data structures."""
  AddArdhasamavrtta('Anuṣṭup (Śloka)', '. . . . L G G .', '. . . . L G L G')
  AddAnustupExamples()

  # AddMatravrtta('Āryā (mātrā)', [12, 18, 12, 15])
  AddAryaExamples()
  AddGitiExamples()

  # Bhartṛhari
  AddSamavrtta('Upajāti', '. G L G G L L G L G G')
  # Bhartṛhari
  AddSamavrtta('Vaṃśastham', 'L G L G G L L G L G L G')
  # AddSamavrtta('Indravaṃśā', 'G G L G G L L G L G L G')
  # Bhartṛhari
  AddSamavrtta('Rathoddhatā', 'G L G L L L G L G L G')
  # AddSamavrtta('Svāgatā', 'G L G L L L G L L G G')
  # Bhartṛhari
  AddSamavrtta('Drutavilambitam', 'L L L G L L G L L G L G')
  # AddSamavrtta('Mañjubhāṣiṇī', 'L L G L G L L L G L G L G')
  # Bhartṛhari
  AddSamavrtta('Śālinī', 'G G G G — G L G G L G G')
  # AddSamavrtta('Praharṣiṇī', 'G G G L L L L G L G L G G')
  # AddSamavrtta('Bhujañgaprayātam', 'L G G L G G L G G L G G')
  # AddSamavrtta('Toṭakam', 'L L G L L G L L G L L G')
  # AddSamavrtta('Sragviṇī', 'G L G G L G G L G G L G')
  # AddSamavrtta('Pramitākṣarā', 'L L G L G L L L G L L G')
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
  # AddArdhasamavrtta('Aupacchandasikam (Vasantamālikā) (Upodgatā)',
  #                   'L L G   L L G L G L G G', 'L L G G L L G L G L G G')
  # AddArdhasamavrtta('Aparavaktrā',
  #                   'L L L L L L G — L G L G', 'L L L L G — L L G L G L G')
  # Bhartṛhari
  AddArdhasamavrtta('Puṣpitāgrā',
                    'L L L L L L G L G L G G', 'L L L L G L L G L G L G G')
  # AddVishamavrtta('Udgatā', ['L L  G  L  G  L L L G L',
  #                             'L L L L L  G  L  G  L G',
  #                             ' G  L L L L L L  G  L L G',
  #                             'L L  G  L  G  L L L  G  L G L G'])
  # AddSamavrtta('Aśvadhāṭī (Sitastavaka?)',
  #              'G G L G L L L – G G L G L L L – G G L G L L L G')
  # AddSamavrtta('Śivatāṇḍava',
  #              'L G L L  L G L L  L G L L  L G L L  L G L L  L G L L  L G')
  # Bhartṛhari
  AddSamavrtta('Dodhakam', 'G L L G L L G L L G G')
  # # AddMatravrtta('Pādākulakam (and many other names)', ['4 * 4'] * 4)
  # AddSamavrtta('Mālatī', 'L L L L G L L G L G L G')
  # AddSamavrtta('Madīrā', 'G L L  G L L  G L L  G L L  G L L  G L L  G L L  G')
  # AddSamavrtta('Matta-mayūram', 'G G G G – G L L G G – L L G G')
  # AddSamavrtta('Vidyunmālā', 'G G G G G G G G')


