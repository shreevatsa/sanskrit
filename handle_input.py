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


def _transliterate_and_clean(orig_text):
  """Transliterates text to SLP1, removing all other characters."""
  pass_through = ' -?'
  ignore = r"""0123456789'".\/$&%{}|!’‘(),""" + 'ऽ।॥०१२३४५६७८९'
  (text, rejects) = transliterate.DetectAndTransliterate(orig_text, pass_through, ignore)
  read.filters.process_rejected_characters(orig_text, rejects)
  clean_text = ''.join(c for c in text if c not in pass_through)
  assert all(c in slp1.ALPHABET for c in clean_text), clean_text
  return (text, clean_text)


def _cleaned_lines_and_display_lines(cleaned_and_display_lines):
  """Separate into two separate lists."""
  while cleaned_and_display_lines and not cleaned_and_display_lines[-1][0]:
    cleaned_and_display_lines = cleaned_and_display_lines[:-1]
  cleaned_lines = [cleaned for (cleaned, display) in cleaned_and_display_lines]
  display_lines = [display for (cleaned, display) in cleaned_and_display_lines]
  return (cleaned_lines, display_lines)


def clean_text(text):
  """The transliterated text from arbitrary input."""
  text = read.filters.normalize_nfkc(text)
  text = read.filters.remove_control_characters(text)
  text = read.filters.process_html(text)
  # TODO(shreevatsa): Replace with a placeholder instead of removing entirely.
  text = read.filters.remove_verse_numbers(text)
  lines = text.strip().splitlines()

  cleaned_and_display_lines = []
  for line in lines:
    (line, clean_line) = _transliterate_and_clean(line)
    cleaned_and_display_lines.append((clean_line, line))
  (cleaned_lines, display_lines) = _cleaned_lines_and_display_lines(cleaned_and_display_lines)

  debug_output = ['Input read as:']
  for (number, display_line) in enumerate(display_lines):
    transliterated = transliterate.TransliterateForOutput(display_line)
    debug_output.append('Line %d: %s' % (number + 1, transliterated))
  debug_output.append('')
  logging.debug('\n'.join(debug_output))

  return (cleaned_lines, display_lines)
