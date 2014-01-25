# -*- coding: utf-8 -*-
"""Data structure that stores the result of a metre matching a known pattern."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


# Poor man's enum for now. Python adds enum support in Python 3.4+.
def Enum(**enums):
  return type(str('Enum'), (), enums)

ISSUES = Enum(UNKNOWN_ISSUE=0,
              VISAMA_PADANTA_LAGHU='viṣama-pādānta-laghu',
              PADANTA_LAGHU='pādānta-laghu',
              FIRST_PADA_OFF='first pāda not conforming',
              THIRD_PADA_OFF='third pāda not conforming'
             )

MATCH_TYPE = Enum(UNKNOWN=0,
                  FULL=1,
                  PADA=2,
                  ODD_PADA=3,
                  EVEN_PADA=4,
                  HALF=5,
                  FIRST_HALF=6,
                  SECOND_HALF=7,
                  PADA_1=8,
                  PADA_2=9,
                  PADA_3=10,
                  PADA_4=11
                 )


class MatchResult(object):
  """Result of match against some known pattern/regex: metre with some info."""

  def __init__(self, metre_name, match_type, issues=None):
    self.metre_name = metre_name
    self.match_type = match_type
    if issues is None:
      self.issues = []
    else:
      assert isinstance(issues, list)
      self.issues = issues

  def __str__(self):
    return self.Name()

  def NameWithMatchType(self):
    assert self.match_type
    return {
        MATCH_TYPE.FULL: '%s',
        MATCH_TYPE.HALF: 'Half of %s',
        MATCH_TYPE.PADA: 'One pāda of %s',
        MATCH_TYPE.ODD_PADA: 'Odd pāda of %s',
        MATCH_TYPE.EVEN_PADA: 'Even pāda of %s',
        MATCH_TYPE.FIRST_HALF: 'First half of %s',
        MATCH_TYPE.SECOND_HALF: 'Second half of %s',
        MATCH_TYPE.PADA_1: 'First pāda of %s',
        MATCH_TYPE.PADA_2: 'Second pāda of %s',
        MATCH_TYPE.PADA_3: 'Third pāda of %s',
        MATCH_TYPE.PADA_4: 'Fourth pāda of %s'
        }[self.match_type] % self.metre_name

  def Name(self):
    """Name of the match, including match type and issues."""
    name = self.NameWithMatchType()
    if self.issues:
      return name + ' (with %s)' % ', '.join(self.issues)
    else:
      return name

  def MetreName(self):
    if self.issues:
      return self.metre_name + ' (with %s)' % ', '.join(self.issues)
    else:
      return self.metre_name

  def MetreNameOnlyBase(self):
    return self.metre_name


# Unless we want to create another type for a list of MatchResults
def Names(match_results):
  return ' AND '.join(m.Name() for m in match_results)


def Description(match_results, indent_depth=0):
  indent = ' ' * indent_depth
  s = ''
  for (i, result) in enumerate(match_results):
    s += indent + 'Result %d: ' % i
    s += '\n' + indent + '\tMetre name: %s' % result.metre_name
    s += '\n' + indent + '\tMatch type: %s' % result.match_type
    s += '\n' + indent + '\tIssues: %s' % result.issues
  return s
