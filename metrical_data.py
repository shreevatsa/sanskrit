#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Functions that deal with the actual data."""

from __future__ import unicode_literals
import re

import simple_utils

# TODO(shreevatsa): Make this pattern -> list, not pattern -> specific pāda type
known_patterns = {}
known_metres = {}


def OptionsExpand(pattern):
  if pattern.find('.') == -1:
    yield pattern
    return
  where = pattern.find('.')
  for fix in ['L', 'G']:
    for y in OptionsExpand(pattern[:where] + fix + pattern[where + 1:]):
      yield y


def AddVrtta(metre_name, verse_pattern):
  known_metres[verse_pattern] = metre_name


def AddSamavrtta(metre_name, each_line_pattern):
  each_line_pattern = CleanUpPatternString(each_line_pattern)
  assert re.match(r'^[LG.]*$', each_line_pattern), each_line_pattern
  AddVrtta(metre_name, each_line_pattern * 4)
  for fully_specified_pattern in OptionsExpand(each_line_pattern):
    known_patterns[fully_specified_pattern] = '%s_pāda' % (metre_name)


def AddArdhasamavrtta(metre_name, odd_line_pattern, even_line_pattern):
  """Given an ardha-sama-vṛtta metre, add it to the data structures."""
  odd_line_pattern = CleanUpPatternString(odd_line_pattern)
  # Odd _pāda_s in Anuṣṭup don't have to end with a guru
  assert re.match(r'^[LG.]*$', odd_line_pattern)
  even_line_pattern = CleanUpPatternString(even_line_pattern)
  assert re.match(r'^[LG.]*$', even_line_pattern)
  AddVrtta(metre_name, (odd_line_pattern + even_line_pattern) * 2)
  for fully_specified_pattern in OptionsExpand(odd_line_pattern):
    known_patterns[fully_specified_pattern] = '%s_pāda_odd' % (metre_name)
  for fully_specified_pattern in OptionsExpand(even_line_pattern):
    known_patterns[fully_specified_pattern] = '%s_pāda_even' % (metre_name)


def AddVishamavrtta(metre_name, line_patterns):
  """Given a viṣama-vṛtta metre, add it to the data structures."""
  assert len(line_patterns) == 4
  verse_pattern = ''
  for i in range(4):
    line_pattern = line_patterns[i]
    line_pattern = CleanUpPatternString(line_pattern)
    # Doesn't have to end in guru; consider pāda 1 of Udgatā
    assert re.match(r'^[LG.]*$', line_pattern)
    verse_pattern += line_pattern
    for fully_specified_pattern in OptionsExpand(line_pattern):
      known_patterns[fully_specified_pattern] = '%s_pāda_%d' % (metre_name, i)
  AddVrtta(metre_name, verse_pattern)


def InitializeData():
  """Add all known metres to the data structures."""
  # TODO(shreevatsa): Ridiculous that this runs each time; needs fixing (easy).
  AddArdhasamavrtta('Anuṣṭup (Śloka)', '. . . . L G G .', '. . . . L G L .')
  # AddMatravrtta('Āryā', '12 + 18 + 12 + 15')
  AddSamavrtta('Upajāti', '. G L G G L L G L G .')
  AddSamavrtta('Vaṃśastham', 'L G L G G L L G L G L .')
  AddSamavrtta('Indravaṃśā', 'G G L G G L L G L G L .')
  AddSamavrtta('Rathoddhatā', 'G L G L L L G L G L .')
  AddSamavrtta('Svāgatā', 'G L G L L L G L L G .')
  AddSamavrtta('Drutavilambitam', 'L L L G L L G L L G L .')
  AddSamavrtta('Mañjubhāṣiṇī', 'L L G L G L L L G L G L .')
  AddSamavrtta('Śālinī', 'G G G G — G L G G L G .')
  AddSamavrtta('Praharṣiṇī', 'G G G L L L L G L G L G .')
  AddSamavrtta('Bhujañgaprayātam', 'L G G L G G L G G L G .')
  AddSamavrtta('Toṭakam', 'L L G L L G L L G L L .')
  AddSamavrtta('Sragviṇī', 'G L G G L G G L G G L .')
  AddSamavrtta('Pramitākṣarā', 'L L G L G L L L G L L .')
  AddSamavrtta('Vasantatilakā', 'G G L G L L L G L L G L G .')
  AddSamavrtta('Mālinī', 'L L L L L L G G — G L G G L G .')
  AddSamavrtta('Cārucāmaram', 'G L G L G L G L G L G L G L .')
  AddSamavrtta('Pañcacāmaram', 'L G L G L G L G L G L G L G L .')
  AddSamavrtta('Mandākrāntā', 'G G G G — L L L L L G — G L G G L G .')
  AddSamavrtta('Śikhariṇī', 'L G G G G G – L L L L L G G — L L L .')
  AddSamavrtta('Hariṇī', 'L L L L L G — G G G G — L G L L G L .')
  AddSamavrtta('Pṛthvī', 'L G L L L G L G—L L L G L G G L .')
  AddSamavrtta('Kokilalam (Nardaṭakam)', 'L L L L G L G L L L G — L L G L L .')
  AddSamavrtta('Mallikāmālā (Matta-kokilā)',
               'G L G L L G L G L L G L G L L G L .')
  AddSamavrtta('Śārdūlavikrīḍitam', 'G G G L L G L G L L L G — G G L G G L .')
  AddSamavrtta('Sragdharā', 'G G G G L G G — L L L L L L G — G L G G L G .')
  AddArdhasamavrtta('Viyoginī', 'L L G   L L G L G L .',
                    'L L G G L L G L G L .')
  AddArdhasamavrtta('Aupacchandasikam (Vasantamālikā) (Upodgatā)',
                    'L L G   L L G L G L G .', 'L L G G L L G L G L G .')
  AddArdhasamavrtta('Aparavaktrā',
                    'L L L L L L G — L G L .', 'L L L L G — L L G L G L .')
  AddArdhasamavrtta('Puṣpitāgrā',
                    'L L L L L L G L G L G .', 'L L L L G L L G L G L G .')
  AddVishamavrtta('Udgatā', ['L L  G  L  G  L L L G L',
                              'L L L L L  G  L  G  L .',   # TODO(shreevatsa): ā
                              ' G  L L L L L L  G  L L .',
                              'L L  G  L  G  L L L  G  L G L .'])
  AddSamavrtta('Aśvadhāṭī (Sitastavaka?)',
               'G G L G L L L – G G L G L L L – G G L G L L L .')
  AddSamavrtta('Śivatāṇḍava',
               'L G L L  L G L L  L G L L  L G L L  L G L L  L G L L  L .')
  AddSamavrtta('Dodhakam', 'G L L G L L G L L G .')
  # AddMatravrtta('Pādākulakam (and many other names)', ['4 * 4'] * 4)
  AddSamavrtta('Mālatī', 'L L L L G L L G L G L .')
  AddSamavrtta('Madīrā', 'G L L  G L L  G L L  G L L  G L L  G L L  G L L  .')
  AddSamavrtta('Matta-mayūram', 'G G G G – G L L G G – L L G .')
  AddSamavrtta('Vidyunmālā', 'G G G G G G G .')


def CleanUpPatternString(pattern):
  return simple_utils.RemoveChars(pattern, ' —–')


