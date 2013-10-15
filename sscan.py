#!/usr/bin/python

import re
import sys

# A regular-expression "character class" for each type
consonant = '[MHkgGcjJTDNtdnpbmyrlvzSsh]'
alpaprana = '[kgcjTDtdpb]'
short_vowel = '[aiuR]'
long_vowel = '[AIUeo]'
vowel = short_vowel.strip(']') + long_vowel.strip('[')


def MassageHK(line):
  """Replace multiple characters with a single one, etc."""
  # Two-letter vowels like ai and au
  line = re.sub('lR', 'R', line)
  line = re.sub('lRR', 'RR', line)
  line = re.sub('RR', 'e', line)
  line = re.sub('a[iu]', 'e', line)
  # Two-letter consonants: replace 'kh' by 'k', etc.
  line = re.sub('(' + alpaprana + ')' + 'h', r'\g<1>', line)
  return line


def MetricalPattern(line):
  # Consonants at beginning of line can be ignored
  line = re.sub('^' + consonant + '+', '', line)
  # A long vowel followed by any number of consonants is a guru
  line = re.sub(long_vowel + consonant + '*', '- ', line)
  # A short vowel followed by multiple (>=2) consonants is a guru
  line = re.sub(short_vowel + consonant + '{2,}', '- ', line)
  # A short vowel followed by a consonant is a laghu
  line = re.sub(short_vowel + consonant + '*', 'u ', line)
  return line

for line in sys.stdin:
  if line.strip() == '':
    print
    continue
  orig_line = line
  line = MassageHK(line)

  # Remove spaces, digits, avagraha, punctuation
  line = line.translate(None, " '$&%{}")
  line = line.translate(None, '0123456789./')

  line = MetricalPattern(line)

  # Remove trailing spaces
  line = line.strip()

  # Currently using a text in Mandakranta (Meghaduta) as testcase
  if line not in ['- - - - u u u u u - - u - - u - -',
                  '- - - - u u u u u - - u - - u - u']:
    print '%s \t \t \t (%s)' % (line.strip(), orig_line.strip())

