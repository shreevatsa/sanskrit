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
  if pattern.endswith('.'):
    logging.warning('Pattern %s is already liberal.', pattern)
  else:
    assert pattern.endswith('G')
  return pattern[:-1] + '.'


def LaghuEnding(pattern):
  assert pattern.endswith('G'), pattern
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
    logging.warning('Not adding %s for %s. It is known as %s', pattern,
                    metre_name, known_patterns[pattern])
  else:
    AddPada(metre_name, pattern)


def AddPada(metre_name, pattern):
  assert re.match(r'^[LG]*$', pattern)
  if pattern in known_patterns:
    logging.warning('Pattern %s, being added for %s, is already known as %s',
                    pattern, metre_name, known_patterns[pattern])
    known_patterns[pattern] += ' or one pāda of %s' % metre_name
    if pattern.endswith('G'):
      MaybeAddPada(metre_name + ' (with pādānta-laghu)', LaghuEnding(pattern))
  else:
    known_patterns[pattern] = 'One pāda of %s' % metre_name
    if pattern.endswith('G'):
      MaybeAddPada(metre_name + ' (with viṣama-pādānta-laghu)',
                   LaghuEnding(pattern))


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


def AddSamavrtta(metre_name, each_line_pattern):
  """Given a sama-vṛtta metre, add it to the data structures."""
  clean = CleanUpPatternString(each_line_pattern)
  assert re.match(r'^[LG.]*$', clean)
  assert clean.endswith('G'), (clean, metre_name)
  if clean.endswith('G'):
    loose = LooseEnding(clean)
    laghu = LaghuEnding(clean)
    full_verse_pattern = (clean + loose) * 2
    AddVrtta(metre_name, full_verse_pattern)
    AddArdha(metre_name, clean, loose)
    for verse_pattern in [clean + loose + laghu + loose,
                          laghu + loose + clean + loose,
                          laghu + loose + laghu + loose]:
      AddVrtta(metre_name + ' (with viṣama-pādānta-laghu)', verse_pattern)
    for explicit_pattern in OptionsExpand(clean):
      AddPada(metre_name, explicit_pattern)


def AddArdhasamavrtta(metre_name, odd_line_pattern, even_line_pattern):
  """Given an ardha-sama-vṛtta metre, add it to the data structures."""
  clean_odd = CleanUpPatternString(odd_line_pattern)
  assert re.match(r'^[LG.]*$', clean_odd)
  clean_even = CleanUpPatternString(even_line_pattern)
  assert re.match(r'^[LG.]*$', clean_even)

  loose_even = LooseEnding(clean_even)
  if clean_odd.endswith('.'):
    # This is the easy case. The pattern itself is already liberal.
    full_verse_pattern = (clean_odd + loose_even) * 2
    AddVrtta(metre_name, full_verse_pattern)
    AddArdha(metre_name, clean_odd, clean_even)
    for explicit_pattern in OptionsExpand(clean_odd):
      AddPada(metre_name + ' (odd pāda)', explicit_pattern)
    for explicit_pattern in OptionsExpand(clean_even):
      AddPada(metre_name + ' (even pāda)', explicit_pattern)
  else:
    assert clean_odd.endswith('G')
    laghu_odd = LaghuEnding(clean_odd)
    full_verse_pattern = (clean_odd + loose_even) * 2
    AddVrtta(metre_name, full_verse_pattern)
    for verse_pattern in [clean_odd + loose_even + laghu_odd + loose_even,
                          laghu_odd + loose_even + clean_odd + loose_even,
                          laghu_odd + loose_even + laghu_odd + loose_even]:
      AddVrtta(metre_name + ' (with viṣama-pādānta-laghu)', verse_pattern)
    AddArdha(metre_name, clean_odd, loose_even)
    for explicit_pattern in OptionsExpand(clean_odd):
      AddPada(metre_name + ' (odd pāda)', explicit_pattern)
    for explicit_pattern in OptionsExpand(clean_even):
      AddPada(metre_name + ' (even pāda)', explicit_pattern)


def AddVishamavrtta(metre_name, line_patterns):
  """Given a viṣama-vṛtta metre, add it to the data structures."""
  assert len(line_patterns) == 4
  verse_pattern = ''
  for i in range(4):
    line_pattern = CleanUpPatternString(line_patterns[i])
    # Doesn't have to end in guru; consider pāda 1 of Udgatā
    assert re.match(r'^[LG.]*$', line_pattern)
    verse_pattern += line_pattern
    for fully_specified_pattern in OptionsExpand(line_pattern):
      known_patterns[fully_specified_pattern] = '%s_pāda_%d' % (metre_name, i)
  AddVrtta(metre_name, verse_pattern)


def AddMatravrtta(metre_name, line_morae):
  known_morae[repr(line_morae)] = metre_name
  if len(line_morae) == 4:
    # Not ideal (lossy), but input is often like this.
    known_morae[repr([line_morae[0] + line_morae[1],
                      line_morae[2] + line_morae[3]])] = metre_name


def InitializeData():
  """Add all known metres to the data structures."""
  # TODO(shreevatsa): Ridiculous that this runs each time; needs fixing (easy).
  AddArdhasamavrtta('Anuṣṭup (Śloka)', '. . . . L G G .', '. . . . L G L .')

  # AddMatravrtta('Āryā', [12, 18, 12, 15])
  # From Bhartrhari (BharSt_1.3)
  AddVishamavrtta('Āryā', ['GGLLGGG', 'LLLLGGLGLGGG', 'GLLLGLGG', 'GGLLGLGLLG'])
  # Should we have this?
  AddVishamavrtta('Āryā (with final laghu)',
                  ['GGLLGGG', 'LLLLGGLGLGGG', 'GLLLGLGG', 'GGLLGLGLLL'])

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
                              'L L L L L  G  L  G  L G',   # TODO(shreevatsa): ā
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
