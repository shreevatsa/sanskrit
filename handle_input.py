# -*- coding: utf-8 -*-

"""Takes the input verse and produces verse lines in SLP1 transliteration."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import logging

import read.filters
import slp1
from transliteration import transliterate


def call_with_log_capture(function, *args, **kwargs):
  """Call the function with args and kwargs, and return both its result and logging."""
  logger = logging.getLogger()
  original_logger_level = logger.level
  original_handler_levels = [handler.level for handler in logger.handlers]
  for handler in logger.handlers:
    handler.setLevel(max(handler.level, original_logger_level))
  logger.setLevel(logging.DEBUG)
  log_capturer_stream = io.StringIO()
  log_capture_handler = logging.StreamHandler(log_capturer_stream)
  log_capture_handler.setLevel(logging.DEBUG)
  logger.addHandler(log_capture_handler)

  return_value = function(*args, **kwargs)

  log_contents = log_capturer_stream.getvalue()
  log_capturer_stream.close()
  logger.removeHandler(log_capture_handler)
  for (i, handler) in enumerate(logger.handlers):
    handler.setLevel(original_handler_levels[i])
  logger.setLevel(original_logger_level)

  if log_contents:
    assert log_contents[-1] == '\n'
    log_contents = log_contents[:-1]
  return (return_value, log_contents)


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
      self.debug_output.append(debug)
      (line, debug) = call_with_log_capture(read.filters.normalize_nfkc, line)
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
    self.debug_output.append('Input read as:')
    for (number, line) in enumerate(display_lines):
      transliterated = transliterate.TransliterateForOutput(line)
      self.debug_output.append('Line %d: %s' % (number + 1, transliterated))
    self.debug_output.append('')
    return (display_lines, cleaned_lines)
