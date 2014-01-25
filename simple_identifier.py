"""A unified interface to reader + scanner + metrical_data + identifier."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import handle_input
import identifier
import metrical_data
import scan


class SimpleIdentifier(object):
  """A single interface to read-scan-identify."""

  def __init__(self):
    if not metrical_data.known_metre_patterns:
      metrical_data.InitializeData()
    self.identifier = identifier.Identifier(metrical_data)

  def _Reset(self):
    self.output = []
    self.cleaned_output = None

  def IdentifyFromLines(self, input_lines):
    """Given bunch of lines of verse, clean-scan-identify."""
    self._Reset()
    logging.info('Got input:\n%s', '\n'.join(input_lines))
    cleaner = handle_input.InputHandler()
    cleaned_lines = cleaner.CleanLines(input_lines)
    self.output.extend(cleaner.error_output)
    self.cleaned_output = cleaner.clean_output

    pattern_lines = scan.ScanVerse(cleaned_lines)
    if not pattern_lines:
      return None

    result = self.identifier.IdentifyFromLines(pattern_lines)
    if not result:
      self.output.extend(cleaner.clean_output)
    return result

  def AllDebugOutput(self):
    return '\n'.join(self.output + self.identifier.output)
