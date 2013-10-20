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


def MetricalPattern(text):
  if not re.match('^[aAiIuUReoMHkgGcjJTDNtdnpbmyrlvzSsh]*$', text):
    print 'Invalid characters in %s' % text
    return None
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

known_metres = {
  'GGGGLLLLLGGLGGLG.': 'mandākrāntā'
  }

def IdentitfyPattern(pattern):
  if not re.match('^[LG]*$', pattern):
    print '%s is not a pattern (must have only L and G)' % pattern
  metre = None
  for known_pattern, known_metre in known_metres.iteritems():
    if re.match('^' + known_pattern + '$', pattern):
      metre = known_metre
      continue
  if not metre:
    print '%s \t \t \t (%s)' % (line.strip(), orig_line.strip())


for line in sys.stdin:
  line = line.strip()
  if not line: continue
  orig_line = line
  line = MassageHK(line)

  # Remove spaces, digits, avagraha, punctuation
  line = line.translate(None, " 0123456789'./$&%{}")

  line = MetricalPattern(line)
  IdentitfyPattern(line)
