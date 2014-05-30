"""A unified interface to reader + scanner + metrical_data + identifier."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import display
import handle_input
import identifier
import metrical_data
import scan


class SimpleIdentifier(object):
  """A single interface to read-scan-data-identify-display."""

  def __init__(self):
    """Initialize whichever of the parts need it."""
    if not metrical_data.known_metre_patterns:
      metrical_data.InitializeData()
    self.identifier = identifier.Identifier(metrical_data)

  def _Reset(self):
    self.debug_read = []
    self.debug_identify = []
    self.tables = []

  def IdentifyFromLines(self, input_lines):
    """Given lines of verse, read-scan-identify-display."""
    self._Reset()
    logging.info('Got input:\n%s', '\n'.join(input_lines))
    input_handler = handle_input.InputHandler()
    (display_lines, cleaned_lines) = input_handler.CleanLines(input_lines)
    self.debug_read.extend(input_handler.debug_output)
    pattern_lines = scan.ScanVerse(cleaned_lines)
    if not pattern_lines:
      return None

    (full_match,
     results) = self.identifier.IdentifyFromPatternLines(pattern_lines)
    self.debug_identify = (['Full:'] + self.identifier.global_info +
                           ['Lines:'] + self.identifier.lines_info +
                           ['Halves:'] + self.identifier.halves_info +
                           ['Quarters:'] + self.identifier.quarters_info)
    if results:
      for m in results:
        known_pattern = metrical_data.GetPattern(m)
        if known_pattern:
          alignment = display.AlignVerseToMetre(display_lines,
                                                ''.join(pattern_lines),
                                                known_pattern)
          table = display.HtmlTableFromAlignment(alignment)
          self.tables.append((m, table))
    return (full_match, results)

  def DebugRead(self):
    return '\n'.join(self.debug_read)

  def DebugIdentify(self):
    return '\n'.join(self.debug_identify)

  def AllDebugOutput(self):
    return '\n'.join([self.debug_read, self.debug_identify])
