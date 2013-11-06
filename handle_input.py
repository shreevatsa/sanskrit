# -*- coding: utf-8 -*-

"""Utils to clean up input."""

from __future__ import unicode_literals

import itertools
import re

import slp1
import transliteration_data


def BreakIntoVerses(input_lines):
  verses = []
  for key, group in itertools.groupby(input_lines, bool):
    if not key:
      continue
    verses.append(list(group))
  return verses


def TransliterateAndClean(text):
  """Transliterates text to SLP1, removing all other characters."""
  orig_text = text
  ignore = r""" 0123456789'".\/$&%{}|-!’""" + 'ऽ।॥०१२३४५६७८९'
  (text, rejects) = transliteration_data.DetectAndTransliterate(text, ignore)

  underline = ''
  bad_chars = []
  if rejects:
    for i in range(len(orig_text)):
      if i in rejects and orig_text[i] not in ignore:
        underline += '^'
        bad_chars.append(orig_text[i])
      else:
        underline += ' '
  if underline.strip():
    print 'Unknown characters are ignored: %s' % (' '.join(bad_chars))
    print orig_text
    print underline

  assert not re.search('[^%s]' % slp1.ALPHABET, text), text
  return text


def CleanLines(lines):
  cleaned_lines = []
  for line in lines:
    line = line.strip()
    if not line: continue
    line = TransliterateAndClean(line)
    cleaned_lines.append(line)
  return cleaned_lines
