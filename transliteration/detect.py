# -*- coding: utf-8 -*-

"""Detecting the input scheme."""

from __future__ import absolute_import, division, print_function, unicode_literals

import re

from poor_enums import Enum
from transliteration import devanagari
from transliteration.transliteration_data import KANNADA_CONSONANTS

TRANSLITERATION_SCHEME = Enum(HK=0,
                              IAST=1,
                              ITRANS=2,
                              Devanagari=3,
                              Kannada=4)


def detect_transliteration_scheme(text):
  """Returns which transliteration scheme the given text is in."""
  characteristic_kannada = '[%s]' % KANNADA_CONSONANTS
  if re.search(characteristic_kannada, text):
    return TRANSLITERATION_SCHEME.Kannada
  characteristic_devanagari = '[%s]' % ''.join(devanagari.Alphabet())
  if re.search(characteristic_devanagari, text):
    return TRANSLITERATION_SCHEME.Devanagari
  characteristic_iast = '[āīūṛṝḷḹṃḥṅñṭḍṇśṣ]'
  if re.search(characteristic_iast, text):
    return TRANSLITERATION_SCHEME.IAST
  characteristic_itrans = (r'aa|ii|uu|[RrLl]\^[Ii]|RR[Ii]|LL[Ii]|~N|Ch|~n|N\^'
                           + r'|Sh|sh')
  if re.search(characteristic_itrans, text):
    return TRANSLITERATION_SCHEME.ITRANS
  return TRANSLITERATION_SCHEME.HK
