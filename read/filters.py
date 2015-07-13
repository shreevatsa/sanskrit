# -*- coding: utf-8 -*-

"""Cleanup transformations: simple functions which take text and return text."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re


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
