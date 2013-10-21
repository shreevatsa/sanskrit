#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Print the metrical pattern of given text."""

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
  # A short vowel followed by a consonant is a laghu
  text = re.sub(short_vowel + consonant + '*', '-', text)
  text = text.translate(string.maketrans('-+', 'LG'))
  return text

known_patterns = {}
known_metres = {}


def OptionsExpand(pattern):
  print 'Called OptionsExpand on %s' % pattern
  if pattern.find('.') == -1:
    print 'Yielding it'
    yield pattern
    return
  where = pattern.find('.')
  for fix in ['L', 'G']:
    for y in OptionsExpand(pattern[:where] + fix + pattern[where + 1:]):
      yield y


def AddSamavrtta(metre_name, each_line_pattern):
  known_metres[each_line_pattern * 4] = metre_name
  for fully_specified_pattern in OptionsExpand(each_line_pattern):
    known_patterns[fully_specified_pattern] = '%s_pāda' % (metre_name)


def IdentitfyPattern(pattern):
  """Given metrical pattern (string of L's and G's), identify metre."""
  if not re.match('^[LG]*$', pattern):
    print '%s is not a pattern (must have only L and G)' % pattern
  return known_patterns.get(pattern, 'unknown')


def IdentifyMetre(verse):
  """Give metrical pattern of entire verse, identify metre."""
  full_verse = ''.join(verse)
  print 'The input has %d syllables' % len(full_verse)

  for known_pattern, known_metre in known_metres.iteritems():
    if re.match('^' + known_pattern + '$', full_verse):
      print 'Identified as %s' % known_metre
      return known_metre

  print 'Metre unknown, trying by lines: '
  for i in range(len(verse)):
    line_i = verse[i]
    print '  Line %d: pattern %s is %s' % (i, line_i, IdentitfyPattern(line_i))


if __name__ == '__main__':
  AddSamavrtta('mandākrāntā', 'GGGGLLLLLGGLGGLG.')
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


