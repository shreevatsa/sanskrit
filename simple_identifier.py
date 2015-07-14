"""A unified interface to reader + scanner + metrical_data + identifier."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from data import metrical_data
import display
import handle_input
import identifier
import scan
from utils.utils import call_with_log_capture


class SimpleIdentifier(object):
  """A single interface to read-scan-data-identify-display."""

  def __init__(self):
    """Initialize whichever of the parts need it."""
    if not metrical_data.known_full_patterns:
      metrical_data.InitializeData()
    self.identifier = identifier.Identifier(metrical_data)

  def _Reset(self):
    self.debug_read = []
    self.debug_identify = []
    self.tables = []

  def IdentifyFromLines(self, input_lines):
    """Given lines of verse, read-scan-identify-display"""
    return self.IdentifyFromText('\n'.join(input_lines))

  def IdentifyFromText(self, input_text):
    """Given text of verse, read-scan-identify-display."""
    self._Reset()
    logging.info('Got input:\n%s', input_text)
    ((display_lines, cleaned_lines), debug_read) = call_with_log_capture(handle_input.clean_text, input_text)
    self.debug_read.append(debug_read)
    pattern_lines = scan.ScanVerse(cleaned_lines)
    if not pattern_lines:
      return None

    results = self.identifier.IdentifyFromPatternLines(pattern_lines)
    self.debug_identify = (['Global:'] + self.identifier.global_debug +
                           ['Parts:'] + self.identifier.parts_debug)
    new_results = []
    if results:
      for m in list(results.get('exact', [])) + list(results.get('partial', [])) + list(results.get('accidental', [])):
        known_pattern = metrical_data.GetPattern(m)
        if known_pattern:
          alignment = display.AlignVerseToMetre(display_lines,
                                                ''.join(pattern_lines),
                                                known_pattern)
          table = display.HtmlTableFromAlignment(alignment)
          self.tables.append((m, table))
        new_results.append(m)
        break
    return ('exact' in results, new_results)

  def DebugRead(self):
    return '\n'.join(self.debug_read)

  def DebugIdentify(self):
    return '\n'.join(self.debug_identify)

  def AllDebugOutput(self):
    return '\n'.join([self.DebugRead(), self.DebugIdentify()])
