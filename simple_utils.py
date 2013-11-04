"""Some simple utility functions used by the other modules."""

from __future__ import unicode_literals


def RemoveChars(input_string, chars):
  """Wrapper function because string.translate != unicode.translate."""
  for char in chars:
    input_string = input_string.replace(char, '')
  return input_string

