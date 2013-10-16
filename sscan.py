#!/usr/bin/python

"""Print the metrical pattern of given text."""

import re
import sys
import string

# A regular-expression "character class" for each type
consonant = '[MHkgGcjJTDNtdnpbmyrlvzSsh]'
alpaprana = '[kgcjTDtdpb]'
short_vowel = '[aiuR]'
long_vowel = '[AIUeo]'
vowel = short_vowel.strip(']') + long_vowel.strip('[')


def MassageHK(text):
  """Replace multiple characters with a single one, etc."""
  # Two-letter vowels like ai and au
  text = re.sub('lR', 'R', text)
  text = re.sub('lRR', 'RR', text)
  text = re.sub('RR', 'e', text)
  text = re.sub('a[iu]', 'e', text)
  # Two-letter consonants: replace 'kh' by 'k', etc.
  text = re.sub('(' + alpaprana + ')' + 'h', r'\g<1>', text)
  return text


def MetricalPattern(text):
  # Consonants at beginning of text can be ignored
  text = re.sub('^' + consonant + '+', '', text)
  # A long vowel followed by any number of consonants is a guru
  text = re.sub(long_vowel + consonant + '*', '- ', text)
  # A short vowel followed by multiple (>=2) consonants is a guru
  text = re.sub(short_vowel + consonant + '{2,}', '- ', text)
  # A short vowel followed by a consonant is a laghu
  text = re.sub(short_vowel + consonant + '*', 'u ', text)
  return text

print 'GGGGLLLLLGGLGGLGG'
for line in sys.stdin:
  line = line.strip()
  if not line: continue
  orig_line = line
  line = MassageHK(line)

  # Remove spaces, digits, avagraha, punctuation
  line = line.translate(None, " 0123456789'./$&%{}")

  line = MetricalPattern(line)
  line = line.translate(string.maketrans('u-', 'LG'))
  line = line.replace(' ', '')

  # Remove trailing spaces
  line = line.strip()

  # Currently using a text in Mandakranta (Meghaduta) as testcase
  if line not in ['GGGGLLLLLGGLGGLGG',
                  'GGGGLLLLLGGLGGLGL']:
    print '%s \t \t \t (%s)' % (line.strip(), orig_line.strip())

