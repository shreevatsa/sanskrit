#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Print the metrical pattern of given text."""

import re
import string
import sys

# A regular-expression "character class" for each type
consonant = '[MHkgGcjJTDNtdnpbmyrlvzSsh]'
alpaprana = '[kgcjTDtdpb]'
short_vowel = '[aiuR]'
long_vowel = '[AIUeo]'
vowel = short_vowel.strip(']') + long_vowel.strip('[')
valid_hk = 'aAiIuUReoMHkgGcjJTDNtdnpbmyrlvzSsh'


def MassageHK(text):
  """Rewrite keeping metre intact (multiple characters -> single char)."""
  # Two-letter vowels like ai and au
  text = re.sub('lR', 'R', text)
  text = re.sub('lRR', 'RR', text)
  text = re.sub('RR', 'e', text)
  text = re.sub('a[iu]', 'e', text)
  # Two-letter consonants: replace 'kh' by 'k', etc.
  text = re.sub('(' + alpaprana + ')' + 'h', r'\g<1>', text)
  return text


def CheckHK(text):
  """Check that a block of text contains only HK characters."""
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

known_patterns = {
    'GGGGLLLLLGGLGGLGL': 'mandākrāntā_pāda',
    'GGGGLLLLLGGLGGLGG': 'mandākrāntā_pāda'
}
known_metres = {
    'GGGGLLLLLGGLGGLG.' * 4: 'mandākrāntā'
}


def IdentitfyPattern(pattern):
  """Given metrical pattern (string of L's and G's), identify metre."""
  if not re.match('^[LG]*$', pattern):
    print '%s is not a pattern (must have only L and G)' % pattern
  return known_patterns.get(pattern)


def IdentifyMetre(verse):
  """Give metrical pattern of entire verse, identify metre."""
  full_verse = ''.join(verse)
  print 'The input has %d syllables' % len(full_verse)

  print 'Trying as a whole: '
  for known_pattern, known_metre in known_metres.iteritems():
    if re.match('^' + known_pattern + '$', full_verse):
      print 'Identified as %s' % known_metre
      return known_metre

  if len(verse) == 4:
    print 'Trying by lines: '
    for i in range(4):
      line_i = verse[i]
      print 'Line %d: pattern %s is %s' % (i, line_i, IdentitfyPattern(line_i))


for line in sys.stdin:
  line = line.strip()
  if not line: continue
  orig_line = line
  line = MassageHK(line)

  # Remove spaces, digits, avagraha, punctuation
  line = line.translate(None, " 0123456789'./$&%{}")

  line = MetricalPattern(line)
  pAda = IdentitfyPattern(line)
  if not pAda:
    print 'Unknown pattern %s \t \t \t (%s)' % (line, orig_line)

