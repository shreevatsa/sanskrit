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


def _process_blanks(cleaned_and_display_lines):
  """What to do with blank lines."""
  cleaned_lines = []
  display_lines = []
  for (clean_line, line) in cleaned_and_display_lines:
    if not clean_line:
      assert clean_line == ''
      # Zero-out lines containing only punctuation. (Is this necessary, though?)
      cleaned_lines.append('')
      display_lines.append('')
      continue
    cleaned_lines.append(clean_line)
    display_lines.append(line)
  while cleaned_lines and not cleaned_lines[-1]:
    cleaned_lines = cleaned_lines[:-1]
    display_lines = display_lines[:-1]
  return (display_lines, cleaned_lines)


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
  (display_lines, cleaned_lines) = _process_blanks(cleaned_and_display_lines)

  debug_output = ['Input read as:']
  for (number, line) in enumerate(display_lines):
    transliterated = transliterate.TransliterateForOutput(line)
    debug_output.append('Line %d: %s' % (number + 1, transliterated))
  debug_output.append('')
  logging.debug('\n'.join(debug_output))

  return (display_lines, cleaned_lines)
