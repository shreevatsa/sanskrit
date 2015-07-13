# -*- coding: utf-8 -*-

"""Cleanup transformations: simple functions which take text and return text."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import re
import unicodedata


def process_html_line_breaks(text):
  """Turns <br> and <BR> into line breaks."""
  # Not using flags=re.IGNORECASE: <bR> <Br> rare, so prefer being conservative.
  text = re.sub('<BR>', '\n', text)
  text = re.sub('<br>', '\n', text)
  return text


def process_html_spaces(text):
  """Replaces each &nbsp; with a space."""
  return re.sub('&nbsp;', ' ', text)


def process_html(text):
  """Runs two filters."""
  text = process_html_spaces(text)
  text = process_html_line_breaks(text)
  return text


def remove_verse_number(line):
  """Strips everything after ॥, ।।, // or || in the line."""
  # return re.subn(r'[/|]{2}[ \d.a-zA-z}_*\-]*[/|]{2}$', '', line)
  for marker in ['॥', '।।', '//', '||']:
    (line, count) = re.subn(re.escape(marker) + '.*', '', line)
    # Don't expect text to have more than one verse-end marker. Break at first.
    if count:
      return (line, count)
  return (line, 0)


def process_rejected_characters(orig_text, rejects):
  """Debug output about rejected characters, with their unicode codepoints and names."""
  assert isinstance(orig_text, unicode)
  def _unicode_notation(char):
    """The U+92ef etc. notation for a character."""
    assert isinstance(char, unicode)
    return '[U+%04x]' % ord(char)
  if not rejects:
    return
  text_read_as = ''.join(_unicode_notation(c) if c in rejects else c for c in orig_text)
  rejects = [(c, _unicode_notation(c), unicodedata.name(c, 'Unknown')) for c in rejects]
  rejects = ', '.join('%s (%s %s)' % reject for reject in rejects)
  logging.debug('Unknown characters are ignored: %s\nin input\n```%s```', rejects, text_read_as)


def normalize_nfkc(text):
  """Normalize text to NFKC."""
  nfkc = unicodedata.normalize('NFKC', text)
  if text != nfkc:
    logging.debug('%s normalized to %s', text, nfkc)
  if nfkc != unicodedata.normalize('NFC', text):
    logging.warning('NFC and NFKC normalizations differ for %s', text)
  return nfkc


def remove_control_characters(text):
  """Remove non-printable (control) characters in text, and warn."""
  text = text.replace('\t', ' ')  # a tab is a control character too
  without_control = ''.join(c for c in text if
                            not unicodedata.category(c).startswith('C'))
  if text != without_control:
    logging.info('''Removed control characters in
    %s
to get
    %s''', text, without_control)
  return without_control
