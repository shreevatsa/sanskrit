# -*- coding: utf-8 -*-

"""Utils to clean up input."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import re
import unicodedata

import slp1
import transliteration_data


def RemoveHTML(text):
  text = re.sub('<BR>', '', text)
  text = re.sub('&nbsp;', ' ', text)
  return text.strip()


def RemoveVerseNumber(text):
  # return re.subn(r'[/|]{2}[ \d.a-zA-z}_*\-]*[/|]{2}$', '', text)
  return re.subn(r'(॥|([|।/])\2).*', '', text)


def BreakIntoVerses(input_lines):
  verses = []
  for key, group in itertools.groupby(input_lines, bool):
    if not key:
      continue
    verses.append(list(group))
  return verses


def UnicodeNotation(c):
  return 'U+%04x' % ord(c)


class InputHandler(object):
  """Class that takes arbitrary input and returns list of clean lines."""

  def __init__(self):
    self.error_output = []
    self.clean_output = []

  def TransliterateAndClean(self, text):
    """Transliterates text to SLP1, removing all other characters."""
    orig_text = text
    ignore = r""" 0123456789'".\/$&%{}|-!’‘(),""" + 'ऽ।॥०१२३४५६७८९'
    (text, rejects) = transliteration_data.DetectAndTransliterate(text, ignore)

    recognized_text = ''
    for c in orig_text:
      if c in rejects:
        recognized_text += '[%s]' % UnicodeNotation(c)
      else:
        recognized_text += c

    if rejects:
      self.error_output.append('Unknown characters are ignored: %s' % (
          ', '.join('%s (%s %s)' %
                    (c, UnicodeNotation(c), unicodedata.name(c, 'Unknown'))
                    for c in rejects)))
      self.error_output.append(orig_text)
      self.error_output.append('recognized as')
      self.error_output.append(recognized_text)

    assert not re.search('[^%s]' % slp1.ALPHABET, text), text
    return text

  def CleanLines(self, lines):
    """Clean up the input lines (strip junk, transliterate, break verses)."""
    cleaned_lines = []
    for line in lines:
      line = RemoveHTML(line).strip()
      if not line:
        continue
      (line, n) = RemoveVerseNumber(line)
      line = self.TransliterateAndClean(line)
      if not line:
        continue
      cleaned_lines.append(line)
      # If verse number was removed, can separate from next verse by blank line.
      if n:
        cleaned_lines.append('')
    while cleaned_lines and not cleaned_lines[-1]:
      cleaned_lines = cleaned_lines[:-1]

    self.clean_output.append('Input read as:')
    for (number, line) in enumerate(cleaned_lines):
      transliterated = transliteration_data.TransliterateForOutput(line)
      self.clean_output.append('Line %d: %s' % (number + 1, transliterated))
    self.clean_output.append('')
    return cleaned_lines
