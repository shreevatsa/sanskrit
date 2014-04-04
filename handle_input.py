# -*- coding: utf-8 -*-

"""Utils to clean up input."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import unicodedata

import slp1
import transliterate


def RemoveHTML(text):
  text = re.sub('<BR>', '', text)
  text = re.sub('&nbsp;', ' ', text)
  return text.strip()


def RemoveVerseNumber(text):
  # return re.subn(r'[/|]{2}[ \d.a-zA-z}_*\-]*[/|]{2}$', '', text)
  return re.subn(r'(॥|([|।/])\2).*', '', text)


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
    (text, rejects) = transliterate.DetectAndTransliterate(text, ignore)

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
      line = line.strip()
      nfc = unicodedata.normalize('NFC', line)
      nfkc = unicodedata.normalize('NFKC', line)
      if not (line == nfc and line == nfkc):
        self.error_output.append('%s normalized to %s' % (line, nfkc) +
                                 (' (itself different from %s)' % nfc
                                  if nfc != nfkc else ''))
        line = nfkc
      # without_control = ''.join(c for c in line if
      #                           not unicodedata.category(c).startswith('C'))
      # if line != without_control:
      #   self.error_output.append('Removed control characters in %s to get %s'
      #                            % (line, without_control))
      #   line = without_control
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
      transliterated = transliterate.TransliterateForOutput(line)
      self.clean_output.append('Line %d: %s' % (number + 1, transliterated))
    self.clean_output.append('')
    return cleaned_lines
