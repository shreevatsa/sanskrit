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

# TODO(shreevatsa): Make this pattern -> list, not pattern -> specific pāda type
known_patterns = {}
known_metres = {}
known_morae = {}


def LooseEnding(pattern):
  assert pattern.endswith('.') or pattern.endswith('G'), pattern
  return pattern[:-1] + '.'


def LaghuEnding(pattern):
  assert pattern.endswith('.') or pattern.endswith('G'), pattern
  return pattern[:-1] + 'L'


def OptionsExpand(pattern):
  """Given pattern with n '.'s, returns all 2^n patterns with L and G only."""
  where = pattern.find('.')
  if where == -1:
    yield pattern
    return
  prefix = pattern[:where]
  for suffix in OptionsExpand(pattern[where + 1:]):
    for fix in ['L', 'G']:
      yield prefix + fix + suffix


def MaybeAddPada(metre_name, pattern):
  assert re.match(r'^[LG]*$', pattern)
  if pattern in known_patterns:
    logging.warning('Not adding %s for %s. It is already known as %s', pattern,
                    metre_name, known_patterns[pattern])
  else:
    AddPada(metre_name, pattern)


def AddPada(metre_name, pattern):
  assert re.match(r'^[LG]*$', pattern)
  if pattern in known_patterns:
    logging.warning('Pattern %s, being added for %s, is already known as %s',
                    pattern, metre_name, known_patterns[pattern])
    known_patterns[pattern] += ' or one pāda of %s' % metre_name
  else:
    known_patterns[pattern] = 'One pāda of %s' % metre_name
  if pattern.endswith('G'):
    MaybeAddPada(metre_name + ' (with pādānta-laghu)', LaghuEnding(pattern))


def AddArdha(metre_name, pattern_odd, pattern_even):
  assert re.match(r'^[LG.]*$', pattern_odd)
  assert re.match(r'^[LG.]*$', pattern_even)
  assert pattern_even.endswith('.')
  odds = OptionsExpand(pattern_odd)
  # Making this a list as we use it twice.
  evens = list(OptionsExpand(pattern_even))
  for (o, e) in itertools.product(odds, evens):
    known_patterns[o + e] = 'Half of %s' % metre_name
  if pattern_odd.endswith('G'):
    odds = OptionsExpand(LaghuEnding(pattern_odd))
    for (o, e) in itertools.product(odds, evens):
      known_patterns[o + e] = (
          'Half of %s (with viṣama-pādānta-laghu)' % metre_name)


def AddVrtta(metre_name, verse_pattern):
  assert verse_pattern not in known_metres, (verse_pattern,
                                             known_metres[verse_pattern])
  logging.debug('Adding metre %s with pattern %s', metre_name, verse_pattern)
  known_metres[verse_pattern] = metre_name


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

  tolerable = []
  if clean[2].endswith('G'):
    tolerable.append(clean[0] + loose[1] + LaghuEnding(clean[2]) + loose[3])
  if clean[0].endswith('G'):
    laghu0 = LaghuEnding(clean[0])
    tolerable.append(laghu0 + loose[1] + clean[2] + loose[3])
    if clean[2].endswith('G'):
      tolerable.append(laghu0 + loose[1] + LaghuEnding(clean[2]) + loose[3])
  for verse_pattern in tolerable:
    AddVrtta(metre_name + ' (with viṣama-pādānta-laghu)', verse_pattern)


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
    AddPada(metre_name + ' (odd pāda)', explicit_pattern)
  for explicit_pattern in OptionsExpand(clean_even):
    AddPada(metre_name + ' (even pāda)', explicit_pattern)


def AddVishamavrtta(metre_name, line_patterns):
  """Given a viṣama-vṛtta metre, add it to the data structures."""
  AddFourLineVrtta(metre_name, line_patterns)
  clean = [CleanUpPatternString(pattern) for pattern in line_patterns]
  AddArdha('First ' + metre_name, clean[0], LooseEnding(clean[1]))
  AddArdha('Second ' + metre_name, clean[2], LooseEnding(clean[3]))
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


def InitializeData():
  """Add all known metres to the data structures."""
  # TODO(shreevatsa): Ridiculous that this runs each time; needs fixing (easy).
  AddArdhasamavrtta('Anuṣṭup (Śloka)', '. . . . L G G .', '. . . . L G L G')
  # "jayanti te sukṛtino..."
  AddExactVrtta('Anuṣṭup (Śloka) (with first pāda not conforming)',
                ['LGLGLLLG', '....LGL.', '....LGG.', '....LGL.'])

  # AddMatravrtta('Āryā', [12, 18, 12, 15])
  # From Bhartrhari (BharSt_1.3, ajñaḥ sukham ārādhyaḥ...)
  AddExactVrtta('Āryā (with final laghu)',
                ['GGLLGGG', 'LLLLGGLGLGGG', 'GLLLGLGG', 'GGLLGLGLLL'])
  AddExactVrtta('Āryā',
                ['GGLLGGG', 'LLLLGGLGLGG.', 'GLLLGLGG', 'GGLLGLGLL.'])
  # From Bhartrhari (BharSt_1.37, siṃhaḥ śiśur api nipatati...)
  AddExactVrtta('Āryā (with final laghu)',
                ['GGLLLLLLLL', 'LLLLLLGLGLLLGG', 'LLLLGGLLG', 'LLLLGGLGGL'])
  AddExactVrtta('Āryā',
                ['GGLLLLLLLL', 'LLLLLLGLGLLLG.', 'LLLLGGLLG', 'LLLLGGLGG.'])
  # From Bhartrhari (BharSt_1.43, dānaṃ bhogo nāśas...)
  AddExactVrtta('Āryā (with final laghu)',
                ['GGGGGG', 'GGLLGLGLGGL', 'GLLGLLGG', 'GLLGGLGLLL'])
  AddExactVrtta('Āryā',
                ['GGGGGG', 'GGLLGLGLGG.', 'GLLGLLGG', 'GLLGGLGLL.'])
  # From Bhartrhari (BharSt_1.61, mṛga-mīna-sajjanānāṃ...)
  AddExactVrtta('Āryā (with final laghu)',
                ['LLGLGLGG', 'LLLLGGLLLLGGG', 'GLLGLLLLG', 'GGLLGLGLLL'])
  AddExactVrtta('Āryā',
                ['LLGLGLGG', 'LLLLGGLLLLGGG', 'GLLGLLLLG', 'GGLLGLGLL.'])
  # From Bhartrhari (BharSt_1.87, chinno 'pi rohati taruḥ...)
  AddExactVrtta('Āryā (with final laghu)',
                ['GGLGLLLG', 'GGLLGLGLGGL', 'LLLLGGGG', 'GGGGLGGL'])
  AddExactVrtta('Āryā',
                ['GGLGLLLG', 'GGLLGLGLGG.', 'LLLLGGGG', 'GGGGLGG.'])

  AddSamavrtta('Upajāti', '. G L G G L L G L G G')
  AddSamavrtta('Vaṃśastham', 'L G L G G L L G L G L G')
  AddSamavrtta('Indravaṃśā', 'G G L G G L L G L G L G')
  AddSamavrtta('Rathoddhatā', 'G L G L L L G L G L G')
  AddSamavrtta('Svāgatā', 'G L G L L L G L L G G')
  AddSamavrtta('Drutavilambitam', 'L L L G L L G L L G L G')
  AddSamavrtta('Mañjubhāṣiṇī', 'L L G L G L L L G L G L G')
  AddSamavrtta('Śālinī', 'G G G G — G L G G L G G')
  AddSamavrtta('Praharṣiṇī', 'G G G L L L L G L G L G G')
  AddSamavrtta('Bhujañgaprayātam', 'L G G L G G L G G L G G')
  AddSamavrtta('Toṭakam', 'L L G L L G L L G L L G')
  AddSamavrtta('Sragviṇī', 'G L G G L G G L G G L G')
  AddSamavrtta('Pramitākṣarā', 'L L G L G L L L G L L G')
  AddSamavrtta('Vasantatilakā', 'G G L G L L L G L L G L G G')
  AddSamavrtta('Mālinī', 'L L L L L L G G — G L G G L G G')
  AddSamavrtta('Cārucāmaram', 'G L G L G L G L G L G L G L G')
  AddSamavrtta('Pañcacāmaram', 'L G L G L G L G L G L G L G L G')
  AddSamavrtta('Mandākrāntā', 'G G G G — L L L L L G — G L G G L G G')
  AddSamavrtta('Śikhariṇī', 'L G G G G G – L L L L L G G — L L L G')
  AddSamavrtta('Hariṇī', 'L L L L L G — G G G G — L G L L G L G')
  AddSamavrtta('Pṛthvī', 'L G L L L G L G—L L L G L G G L G')
  AddSamavrtta('Kokilalam (Nardaṭakam)', 'L L L L G L G L L L G — L L G L L G')
  AddSamavrtta('Mallikāmālā (Matta-kokilā)',
               'G L G L L G L G L L G L G L L G L G')
  AddSamavrtta('Śārdūlavikrīḍitam', 'G G G L L G L G L L L G — G G L G G L G')
  AddSamavrtta('Sragdharā', 'G G G G L G G — L L L L L L G — G L G G L G G')
  AddArdhasamavrtta('Viyoginī', 'L L G   L L G L G L G',
                    'L L G G L L G L G L G')
  AddArdhasamavrtta('Aupacchandasikam (Vasantamālikā) (Upodgatā)',
                    'L L G   L L G L G L G G', 'L L G G L L G L G L G G')
  AddArdhasamavrtta('Aparavaktrā',
                    'L L L L L L G — L G L G', 'L L L L G — L L G L G L G')
  AddArdhasamavrtta('Puṣpitāgrā',
                    'L L L L L L G L G L G G', 'L L L L G L L G L G L G G')
  AddVishamavrtta('Udgatā', ['L L  G  L  G  L L L G L',
                              'L L L L L  G  L  G  L G',
                              ' G  L L L L L L  G  L L G',
                              'L L  G  L  G  L L L  G  L G L G'])
  AddSamavrtta('Aśvadhāṭī (Sitastavaka?)',
               'G G L G L L L – G G L G L L L – G G L G L L L G')
  AddSamavrtta('Śivatāṇḍava',
               'L G L L  L G L L  L G L L  L G L L  L G L L  L G L L  L G')
  AddSamavrtta('Dodhakam', 'G L L G L L G L L G G')
  # AddMatravrtta('Pādākulakam (and many other names)', ['4 * 4'] * 4)
  AddSamavrtta('Mālatī', 'L L L L G L L G L G L G')
  AddSamavrtta('Madīrā', 'G L L  G L L  G L L  G L L  G L L  G L L  G L L  G')
  AddSamavrtta('Matta-mayūram', 'G G G G – G L L G G – L L G G')
  AddSamavrtta('Vidyunmālā', 'G G G G G G G G')


def CleanUpPatternString(pattern):
  pattern = simple_utils.RemoveChars(pattern, ' —–')
  assert re.match(r'^[LG.]*$', pattern), pattern
  return pattern
