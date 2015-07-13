# -*- coding: utf-8 -*-

"""Takes the input verse and produces verse lines in SLP1 transliteration."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import read.filters
import slp1
from transliteration import transliterate
from utils.utils import call_with_log_capture


class InputHandler(object):
  """Class that takes arbitrary input and returns list of clean lines."""

  def __init__(self):
    self.debug_output = []

  def _transliterate_and_clean(self, orig_text):
    """Transliterates text to SLP1, removing all other characters."""
    pass_through = ' -?'
    ignore = r"""0123456789'".\/$&%{}|!’‘(),""" + 'ऽ।॥०१२३४५६७८९'
    (text, rejects) = transliterate.DetectAndTransliterate(orig_text, pass_through, ignore)
    (_, debug) = call_with_log_capture(read.filters.process_rejected_characters, orig_text, rejects)
    if debug:
      self.debug_output.append(debug)
    clean_text = ''.join(c for c in text if c not in pass_through)
    assert all(c in slp1.ALPHABET for c in clean_text), clean_text
    return (text, clean_text)

  def CleanLines(self, lines):
    """Clean up the input lines (strip junk, transliterate, break verses)."""
    cleaned_lines = []
    display_lines = []
    for line in lines:
      line = line.strip()
      (line, debug) = call_with_log_capture(read.filters.remove_control_characters, line)
      if debug:
        self.debug_output.append(debug)
      (line, debug) = call_with_log_capture(read.filters.normalize_nfkc, line)
      if debug:
        self.debug_output.append(debug)
      line = read.filters.process_html(line).strip()
      (line, n) = read.filters.remove_verse_number(line)
      (line, clean_line) = self._transliterate_and_clean(line)
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

    debug_output = ['Input read as:']
    for (number, line) in enumerate(display_lines):
      transliterated = transliterate.TransliterateForOutput(line)
      debug_output.append('Line %d: %s' % (number + 1, transliterated))
    debug_output.append('')
    logging.debug('\n'.join(debug_output))
    return (display_lines, cleaned_lines)
