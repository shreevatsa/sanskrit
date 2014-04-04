# -*- coding: utf-8 -*-
"""Utilities for normalizing Devanāgari.

The issue is that Unicode Devanāgari includes the "implicit a": for instance it
represents 'ki' as 'ka + vowel sign i' and 'k' as 'ka + virāma'. This requires
special handling of vowel signs, and also special handling when the vowel is a.
So for internal work, we "normalize" all Devanāgari text to a form we call
"Mangled Devanāgari", wherein all (consonant + vowel sign) combinations are
represented internally as (consonant + virāma + vowel) [not vowel sign], even
when the vowel is 'a'.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import re


_CONSONANTS = 'कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह'
_CONSONANT_RE = '[%s]' % _CONSONANTS
_VOWEL_A = 'अ'
_VOWELS_NON_A = 'आइईउऊऋॠऌॡएऐओऔ'
_VOWEL_SIGNS = ['ा', 'ि', 'ी', 'ु', 'ू', 'ृ', 'ॄ', 'ॢ', 'ॣ', 'े', 'ै', 'ो', 'ौ']
_VOWEL_SIGNS_STR = ''.join(_VOWEL_SIGNS)
_VOWEL_SIGNS_RE = '[%s]' % _VOWEL_SIGNS_STR
_ANUSVARA_VISARGA = 'ंः'
_VIRAMA = '्'


def Alphabet():
  return list(_VOWEL_A + _VOWELS_NON_A +
              _ANUSVARA_VISARGA) + [s + _VIRAMA for s in _CONSONANTS]


def Mangle(text):
  """Normalize standard Devanāgari to Mangled Devanāgari."""
  orig_text = text

  signs_to_vowels = dict(zip(_VOWEL_SIGNS, _VOWELS_NON_A))
  # TODO(shreevatsa): Remove this assert; enough confidence
  assert signs_to_vowels == dict(zip(_VOWEL_SIGNS_STR, _VOWELS_NON_A))

  # consonant + vowel sign -> consonant + virāma + vowel
  def Replacer(match):
    return match.group(1) + _VIRAMA + signs_to_vowels[match.group(2)]
  text = re.sub('(%s)([%s])' % (_CONSONANT_RE, _VOWEL_SIGNS_STR),
                Replacer,
                text)
  # Check that no more vowel signs exist
  if re.search(_VOWEL_SIGNS_RE, text):
    logging.error('Error in Devanāgari text %s: Stray vowel signs.', orig_text)

  # consonant + [not virāma] -> consonant + virāma + 'a'
  text = re.sub('(%s)(?!%s)' % (_CONSONANT_RE, _VIRAMA),
                r'\g<1>%s%s' % (_VIRAMA, _VOWEL_A),
                text)
  # Check that no more consonants exist that are not followed by virāma
  for c in re.finditer(_CONSONANT_RE, text):
    assert text[c.start() + 1] == _VIRAMA, (text, c.start())

  assert orig_text == UnMangle(text), (orig_text, text, UnMangle(text))
  logging.debug('Mangled to: %s', text)
  return text


def UnMangle(text):
  """Converts normalized (Mangled) Devanāgari to standard Devanāgari."""
  # consonant + virāma + vowel -> consonant + vowel sign
  vowels = _VOWEL_A + _VOWELS_NON_A
  vowel_re = '[%s]' % vowels
  vowels_to_signs = dict(zip(vowels, [''] + _VOWEL_SIGNS))
  text = re.sub('(%s)%s([%s])' % (_CONSONANT_RE, _VIRAMA, vowel_re),
                lambda match: match.group(1) + vowels_to_signs[match.group(2)],
                text)
  return text
