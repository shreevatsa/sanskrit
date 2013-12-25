#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Data structures that store matching metres for known patterns."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest

import metrical_data
import sscan

identifier = sscan.Identifier()


class BadInput(unittest.TestCase):
  def __init__(self, *args, **kwargs):
    super(BadInput, self).__init__(*args, **kwargs)

  def testEmpty(self):
    """Identifier should fail with empty input."""
    # self.assertRaises(self.identifier.EmptyInputError,
    #                   self.identifier.IdentifyFromLines, [])
    self.assertEqual(identifier.IdentifyFromLines([]), None)

  def testNoSyllables(self):
    """Identifier should return no result, for input containing no syllabes."""
    self.assertEqual(identifier.IdentifyFromLines(['t', 't', 't', 't']), None)


class KnownValues(unittest.TestCase):
  def __init__(self, *args, **kwargs):
    super(KnownValues, self).__init__(*args, **kwargs)
    self.addTypeEqualityFunc(metrical_data.MatchResult, self.MatchResultEqual)

  def MatchResultEqual(self, m1, m2, unused_msg=None):
    if m1.metre_name != m2.metre_name:
      raise self.failureException('Metre names unequal: %s != %s' % (
          m1.metre_name, m2.metre_name))
    if m1.match_type != m2.match_type:
      raise self.failureException('Match types unequal: %s != %s' % (
          m1.match_type, m2.match_type))
    if m1.issues != m2.issues:
      raise self.failureException('Issues unequal: %s != %s' % (m1.issues,
                                                                m2.issues))

  def testFineAnustup(self):
    """Good anuṣṭup must be recognized."""
    verse = ['agajānana padmārkaṃ gajānanam aharniṣam anekadantam bhaktānām',
             'ekadantam upāsmahe']
    self.MatchResultEqual(
        identifier.IdentifyFromLines(verse)[0],
        metrical_data.MatchResult('Anuṣṭup (Śloka)',
                                  metrical_data.MATCH_TYPE.FULL))


if __name__ == '__main__':
  unittest.main()
