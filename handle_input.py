# -*- coding: utf-8 -*-

"""Takes the input verse and produces verse lines in SLP1 transliteration."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import read.filters
import slp1
import transliteration.detect
from transliteration import transliterate


def _transliterate_and_clean(orig_line, input_scheme):
  """Transliterates text to SLP1, removing all other characters."""
  pass_through = ' -?'
  (display_line, rejects) = transliterate.TransliterateFrom(orig_line, input_scheme, pass_through)

  ignore = r"""0123456789'".\/$&%{}|!’‘(),""" + 'ऽ।॥०१२३४५६७८९'
  read.filters.debug_rejected_characters(orig_line, rejects - set(ignore))
  cleaned_line = ''.join(c for c in display_line if c not in pass_through)
  assert all(c in slp1.ALPHABET for c in cleaned_line), cleaned_line
  return (display_line, cleaned_line)


def _preprocess_for_transliteration(text):
  """Clean up text before transliterating."""
  text = read.filters.normalize_nfkc(text)
  text = read.filters.remove_control_characters(text)
  text = read.filters.process_html(text)
  # TODO(shreevatsa): Replace with a placeholder instead of removing entirely.
  text = read.filters.remove_verse_numbers(text)
  text = text.strip('\n')
  return text

def read_text(text):
  """The transliterated text from arbitrary input."""
  text = _preprocess_for_transliteration(text)
  input_scheme = transliteration.detect.detect_transliteration_scheme(text)
  cleaned_lines = []
  display_lines = []
  for line in text.splitlines():
    (display_line, cleaned_line) = _transliterate_and_clean(line, input_scheme)
    cleaned_lines.append(cleaned_line)
    display_lines.append(display_line)
  while cleaned_lines and not cleaned_lines[-1]:
    cleaned_lines = cleaned_lines[:-1]
    display_lines = display_lines[:-1]

  debug_output = ['Input read as:']
  for (number, display_line) in enumerate(display_lines):
    transliterated = transliterate.TransliterateForOutput(display_line)
    debug_output.append('Line %d: %s' % (number + 1, transliterated))
  debug_output.append('')
  logging.debug('\n'.join(debug_output))

  return (cleaned_lines, display_lines)
