#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Print the metrical pattern of given text.

Known issues:
     (1) Needs better treatment of pādānta-guru / pādānta-yati.
     (2) Needs a lot more data (metres).
     (3) Can improve description of metres.
     (4) When analyzing line-by-line, would be nice to show all resolutions.
"""

import re
import string
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
  text = text.translate(string.maketrans('-+', 'LG'))
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


def CleanUpPatternString(pattern):
  return pattern.translate(None, ' —–')


def AddVrtta(metre_name, verse_pattern):
  known_metres[verse_pattern] = metre_name


def AddSamavrtta(metre_name, each_line_pattern):
  each_line_pattern = CleanUpPatternString(each_line_pattern)
  assert re.match(r'^[LG.]*G$', each_line_pattern), each_line_pattern
  AddVrtta(metre_name, each_line_pattern * 4)
  for fully_specified_pattern in OptionsExpand(each_line_pattern):
    known_patterns[fully_specified_pattern] = '%s_pāda' % (metre_name)


def AddArdhasamavrtta(metre_name, odd_line_pattern, even_line_pattern):
  """Given an ardha-sama-vṛtta metre, add it to the data structures."""
  odd_line_pattern = CleanUpPatternString(odd_line_pattern)
  # Odd _pāda_s in Anuṣṭup don't have to end with a guru
  assert re.match(r'^[LG.]*$', odd_line_pattern)
  even_line_pattern = CleanUpPatternString(even_line_pattern)
  assert re.match(r'^[LG.]*G$', even_line_pattern)
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


if __name__ == '__main__':
  AddArdhasamavrtta('Anuṣṭup', '. . . . L G G .', '. . . . L G L G')
  # AddMatravrtta('Āryā', '12 + 18 + 12 + 15')
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

  lines = sys.stdin.readlines()
  pattern_lines = []
  for line in lines:
    line = line.strip()
    if not line: continue
    orig_line = line
    line = MassageHK(line)

    # Remove spaces, digits, avagraha, punctuation
    line = line.translate(None, " 0123456789'./$&%{}")

    pattern_lines.append(MetricalPattern(line))

  identified_metre = IdentifyMetre(pattern_lines)


