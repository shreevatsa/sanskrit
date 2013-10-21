#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Print the metrical pattern of given text.

Usage:
     python sscan.py
     [input verse]
     Ctrl-D

     or

     python sscan.py < input_file

Known issues:
     (1) Needs better treatment of pādānta-guru / pādānta-yati.
     (2) Needs a lot more data (metres).
     (3) Missing in output: description of metres.
     (4) When analyzing line-by-line, would be nice to show all resolutions.
"""

import re
import sys


def MassageHK(text):
  """Rewrite keeping metre intact (multiple characters -> single char)."""
  # Two-letter vowels like ai and au
  text = re.sub('lR', 'R', text)
  text = re.sub('lRR', 'RR', text)
  text = re.sub('RR', 'e', text)
  text = re.sub('a[iu]', 'e', text)
  # Two-letter consonants: replace 'kh' by 'k', etc.
  alpaprana = '[kgcjTDtdpb]'
  text = re.sub('(' + alpaprana + ')' + 'h', r'\g<1>', text)
  return text


def CheckHK(text):
  """Check that a block of text contains only HK characters."""
  valid_hk = 'aAiIuUReoMHkgGcjJTDNtdnpbmyrlvzSsh'
  bad_match = re.search('[^%s]' % valid_hk, text)
  if bad_match:
    first_index = bad_match.start()
    print 'Found non-HK character in text:'
    print text
    print ' ' * first_index + '^'
    return False
  return True


def MetricalPattern(text):
  """Given text in HK, print its metrical pattern (string of 'L's and 'G's)."""
  assert CheckHK(text)
  # A regular-expression "character class" for each type
  consonant = '[MHkgGcjJTDNtdnpbmyrlvzSsh]'
  short_vowel = '[aiuR]'
  long_vowel = '[AIUeo]'
  # vowel = short_vowel.strip(']') + long_vowel.strip('[')
  # Consonants at beginning of text can be ignored
  text = re.sub('^' + consonant + '+', '', text)
  # A long vowel followed by any number of consonants is a guru
  text = re.sub(long_vowel + consonant + '*', '+', text)
  # A short vowel followed by multiple (>=2) consonants is a guru
  text = re.sub(short_vowel + consonant + '{2,}', '+', text)
  # If the line ends in a consonant, the last syllable is a guru
  # TODO(shreevatsa): This requires refinement
  text = re.sub(short_vowel + consonant + '$', '+', text)
  # A short vowel followed by a consonant is a laghu
  text = re.sub(short_vowel + consonant + '*', '-', text)
  assert re.match('^[+-]*$', text)
  text = text.replace('-', 'L')
  text = text.replace('+', 'G')
  assert re.match('^[LG]*$', text)
  return text

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


def RemoveChars(input_string, chars):
  """Wrapper function because string.translate != unicode.translate."""
  for char in chars:
    input_string = input_string.replace(char, '')
  return input_string


def CleanUpPatternString(pattern):
  return RemoveChars(pattern, ' —–')


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


def IdentitfyPattern(pattern):
  """Given metrical pattern (string of L's and G's), identify metre."""
  if not re.match('^[LG]*$', pattern):
    print '%s is not a pattern (must have only L and G)' % pattern
  return known_patterns.get(pattern, 'unknown')


def IdentifyMetre(verse):
  """Give metrical pattern of entire verse, identify metre."""
  full_verse = ''.join(verse)
  print 'The input has %d syllables.' % len(full_verse)

  for known_pattern, known_metre in known_metres.iteritems():
    if re.match('^' + known_pattern + '$', full_verse):
      # print 'Identified as %s, which has pattern:\n    "%s"' % (known_metre,
      #                                                           known_pattern)
      print 'Identified as %s.' % known_metre
      return known_metre

  print 'Metre unknown, trying by lines: '
  for i in range(len(verse)):
    line_i = verse[i]
    print '  Line %d: pattern %s is %s' % (i, line_i, IdentitfyPattern(line_i))


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


def IdentifyFromLines(input_lines):
  """Take a bunch of verse lines (in HK) as input, and identify metre."""
  pattern_lines = []
  for line in input_lines:
    line = line.strip()
    if not line: continue
    line = MassageHK(line)
    # Remove spaces, digits, avagraha, punctuation
    line = RemoveChars(line, " 0123456789'./$&%{}")
    pattern_lines.append(MetricalPattern(line))
  return IdentifyMetre(pattern_lines)


if __name__ == '__main__':
  InitializeData()
  lines = sys.stdin.readlines()
  IdentifyFromLines(lines)
