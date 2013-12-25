#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Data structures that store matching metres for known patterns."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest

import identifier
import match_result


class BadInput(unittest.TestCase):
  def __init__(self, *args, **kwargs):
    super(BadInput, self).__init__(*args, **kwargs)
    self.identifier = identifier.Identifier()

  def testEmpty(self):
    """Identifier should fail with empty input."""
    # self.assertRaises(identifier.EmptyInputError,
    #                   self.identifier.IdentifyFromLines, [])
    self.assertIsNone(self.identifier.IdentifyFromLines([]))

  def testNoSyllables(self):
    """Identifier should return no result, for input containing no syllabes."""
    self.assertIsNone(self.identifier.IdentifyFromLines(['t', 't', 't', 't']))


class KnownValues(unittest.TestCase):
  def __init__(self, *args, **kwargs):
    super(KnownValues, self).__init__(*args, **kwargs)
    self.identifier = identifier.Identifier()

  def AssertSingleMatchResultEquals(self, results, metre_name, match_type,
                                    issues):
    assert isinstance(results, list)
    assert len(results) == 1
    result = results[0]
    assert result.metre_name == metre_name
    assert result.match_type == match_type
    assert result.issues == issues

  def testFineAnustup(self):
    """Good anuṣṭup must be recognized."""
    verse = ['agajānana padmārkaṃ gajānanam aharniṣam anekadantam',
             'bhaktānām ekadantam upāsmahe']
    self.AssertSingleMatchResultEquals(identifier.IdentifyFromLines(verse),
                                       'Anuṣṭup (Śloka)',
                                       match_result.MATCH_TYPE.FULL,
                                       [])


if __name__ == '__main__':
  unittest.main()
