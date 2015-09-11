"""A unified interface to reader + scanner + metrical_data + identifier."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from data import metrical_data
import display
from identify import identifier
from read import read
import scan
from utils.utils import call_with_log_capture


class IdentifierPipeline(object):
  """A single interface to read-scan-data-identify-display."""

  def __init__(self):
    """Initialize whichever of the parts need it."""
    if not metrical_data.known_full_patterns:
      metrical_data.InitializeData()
    self.identifier = identifier.Identifier(metrical_data)

  def _Reset(self):
    self.debug_read = None
    self.debug_identify = []
    self.tables = []

  def IdentifyFromLines(self, input_lines):
    """Given lines of verse, read-scan-identify-display"""
    return self.IdentifyFromText('\n'.join(input_lines))

  def IdentifyFromText(self, input_text):
    """Given text of verse, read-scan-identify-display."""
    self._Reset()
    logging.info('Got input:\n%s', input_text)
    ((cleaned_lines, display_lines), self.debug_read) = call_with_log_capture(read.read_text, input_text)
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
    return self.debug_read or ''

  def DebugIdentify(self):
    return '\n'.join(self.debug_identify)

  def AllDebugOutput(self):
    return '\n'.join([self.DebugRead(), self.DebugIdentify()])
