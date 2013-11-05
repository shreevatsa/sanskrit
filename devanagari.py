# -*- coding: utf-8 -*-

"""Utility for normalising Devanagari module.

The wrinkle here is that Unicode Devanāgari stores 'ki' as 'ka+vowel sign i' and
'k' as 'ka + virāma' etc.
"""


from __future__ import unicode_literals

import logging
import re


def NonAVowels():
  return 'आइईउऊऋॠऌॡएऐओऔ'


def VowelSigns():
  return ['ा', 'ि', 'ी', 'ु', 'ू', 'ृ', 'ॄ', 'ॢ', 'ॣ', 'े', 'ै', 'ो', 'ौ']


def Virama():
  return '्'


def Consonants():
  return 'कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह'


def Alphabet():
  return list('अ' + NonAVowels() + 'ंः') + [s + Virama() for s in Consonants()]


def Mangle(text):
  """Normalises text in Devanāgari."""
  orig_text = text
  consonants = '[' + Consonants() + ']'
  vowel_signs = ''.join(VowelSigns())
  vowels = NonAVowels()
  signs_to_vowels = dict(zip(vowel_signs, vowels))
  virama = Virama()

  # consonant + vowel sign -> consonant + virāma + vowel
  def Replacer(match):
    return match.group(1) + virama + signs_to_vowels[match.group(2)]
  text = re.sub('(' + consonants + ')([' + vowel_signs + '])', Replacer, text)
  # Check that no more vowel signs exist
  if re.search(vowel_signs, text):
    logging.error('Error in Devanāgari text: Stray vowel signs.')
    return None

  # consonant + [not virama] -> consonant + virama + 'a'
  text = re.sub('(' + consonants + ')([^' + virama + '])',
                r'\g<1>' + virama + 'अ' + r'\g<2>', text)
  text = re.sub('(' + consonants + ')$', r'\g<1>' + virama + 'अ', text)
  # Check that no more consonants exist that are not followed by space
  for c in re.finditer(consonants, text):
    assert text[c.start() + 1] == virama

  assert orig_text == UnMangle(text), (orig_text, text, UnMangle(text))
  return text


def UnMangle(text):
  """Converts normalized Devanagari to standard Devanagari."""
  # consonant + virāma + vowel -> consonant + vowel sign
  consonant = '[' + Consonants() + ']'
  vowels = 'अ' + NonAVowels()
  vowel_signs = [''] + VowelSigns()
  vowels_to_signs = dict(zip(vowels, vowel_signs))
  def Replacer(match):
    return match.group(1) + vowels_to_signs[match.group(2)]
  text = re.sub('(' + consonant + ')' + Virama() + '([' + vowels + '])',
                Replacer, text)
  return text
