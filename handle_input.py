# -*- coding: utf-8 -*-

"""Takes the input verse and produces verse lines in SLP1 transliteration."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import re
import unicodedata

import slp1
import transliterate


def RemoveHTML(text):
  text = re.sub('<BR>', '', text)
  text = re.sub('<br>', '', text)
  text = re.sub('&nbsp;', ' ', text)
  return text.strip()


def RemoveVerseNumber(text):
  # return re.subn(r'[/|]{2}[ \d.a-zA-z}_*\-]*[/|]{2}$', '', text)
  return re.subn(r'(॥|([|।/])\2).*', '', text)


def _UnicodeNotation(c):
  assert isinstance(c, unicode)
  return '[U+%04x]' % ord(c)


class InputHandler(object):
  """Class that takes arbitrary input and returns list of clean lines."""

  def __init__(self):
    self.debug_output = []

  def TransliterateAndClean(self, orig_text):
    """Transliterates text to SLP1, removing all other characters."""
    pass_through = ' -?'
    ignore = r"""0123456789'".\/$&%{}|!’‘(),""" + 'ऽ।॥०१२३४५६७८९'
    (text, rejects) = transliterate.DetectAndTransliterate(orig_text,
                                                           pass_through, ignore)
    recognized_text = ''.join(_UnicodeNotation(c) if c in rejects else c
                              for c in orig_text)
    if rejects:
      self.debug_output.append('Unknown characters are ignored: %s' % (
          ', '.join('%s (%s %s)' %
                    (c, _UnicodeNotation(c), unicodedata.name(c, 'Unknown'))
                    for c in rejects)))
      self.debug_output.append('in input')
      self.debug_output.append(recognized_text)
    clean_text = ''.join(c for c in text if c not in pass_through)
    assert all(c in slp1.ALPHABET for c in clean_text), clean_text
    return (text, clean_text)

  def CleanLines(self, lines):
    """Clean up the input lines (strip junk, transliterate, break verses)."""
    # These two functions are here so that they can add to self.debug_output
    def NFKC(line):
      nfkc = unicodedata.normalize('NFKC', line)
      if line != nfkc:
        self.debug_output.append('%s normalized to %s' % (line, nfkc))
      if nfkc != unicodedata.normalize('NFC', line):
        logging.warning('NFC and NFKC normalizations differ for %s', line)
      return nfkc
    def NoControlCharacters(line):
      line = line.replace('\t', ' ')  # a tab is a control character too
      without_control = ''.join(c for c in line if
                                not unicodedata.category(c).startswith('C'))
      if line != without_control:
        self.debug_output.append('Removed control characters in')
        self.debug_output.append('    %s' % line)
        self.debug_output.append('to get')
        self.debug_output.append('    %s' % without_control)
      return without_control
    cleaned_lines = []
    display_lines = []
    for line in lines:
      line = NoControlCharacters(line)
      line = NFKC(line)
      line = RemoveHTML(line).strip()
      (line, n) = RemoveVerseNumber(line)
      (line, clean_line) = self.TransliterateAndClean(line)
      if not clean_line:
        cleaned_lines.append('')
        display_lines.append('')
        continue
      cleaned_lines.append(clean_line)
      display_lines.append(line)
      # If verse number was removed, can separate from next verse by blank line.
      if n:
        cleaned_lines.append('')
        display_lines.append('')
    while cleaned_lines and not cleaned_lines[-1]:
      cleaned_lines = cleaned_lines[:-1]
      display_lines = display_lines[:-1]
    self.debug_output.append('Input read as:')
    for (number, line) in enumerate(display_lines):
      transliterated = transliterate.TransliterateForOutput(line)
      self.debug_output.append('Line %d: %s' % (number + 1, transliterated))
    self.debug_output.append('')
    return (display_lines, cleaned_lines)
