#!/usr/bin/python

import sys, re

# A regular-expression "character class" for each type
consonant = '[MHkgGcjJTDNtdnpbmyrlvzSsh]'
alpaprana = '[kgcjTDtdpb]'
short_vowel = '[aiuR]'
long_vowel = '[AIUeo]'
vowel = short_vowel.strip(']') + long_vowel.strip('[')

for line in sys.stdin.readlines():
  if line.strip() == '':
    print
    continue
  orig_line = line
  # Two-letter vowels like ai and au
  line = re.sub('lR', 'R', line)
  line = re.sub('lRR', 'RR', line)
  line = re.sub('RR', 'e', line)
  line = re.sub('a[iu]', 'e', line)     # Two-letter vowels

  # Remove spaces, digits, avagraha, punctuation
  line = line.translate(None, " '$&%{}")
  line = line.translate(None, '0123456789./')

  # Two-letter consonants: replace 'kh' by 'k', etc.
  line = re.sub('(' + alpaprana + ')' + 'h', '\g<1>', line)

  # Initial consonants
  line = re.sub('^' + consonant + '+', '', line)

  # A long vowel followed by any number of consonants is a guru
  line = re.sub(long_vowel + consonant + '*', '- ', line)
  # print 'After replacing V   : ', line

  # A short vowel followed by multiple (>=2) consonants is a guru
  line = re.sub(short_vowel + consonant + '{2,}', '- ', line)
  # print 'After replacing VCC : ', line

  # A short vowel followed by a consonant is a laghu
  line = re.sub(short_vowel + consonant + '*', 'u ', line)

  # Remove trailing spaces
  line = line.strip();

  # Currently using a text in Mandakranta (Meghaduta) as testcase
  if line not in ['- - - - u u u u u - - u - - u - -',
                  '- - - - u u u u u - - u - - u - u']:
    print '%s \t \t \t (%s)' % (line.strip(), orig_line.strip())


  

  
  
 
    
