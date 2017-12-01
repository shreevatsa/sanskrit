#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for display."""

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import display


class KnownValues(unittest.TestCase):

  def testKnown(self):
    self.assertEqual(display._Align('abcab', 'bca'),
                     ('abcab', '-bca-'))
    self.assertEqual(display._Align('hello', 'hello'),
                     ('hello', 'hello'))
    self.assertEqual(display._Align('hello', 'hell'),
                     ('hello', 'hell-'))
    self.assertEqual(display._Align('hello', 'ohell'),
                     ('-hello', 'ohell-'))
    self.assertEqual(display._Align('abcdabcd', 'abcd'),
                     ('abcdabcd', 'abcd----'))
    self.assertEqual(display._Align('abcab', 'acb'),
                     ('abcab', 'a-c-b'))
    self.assertEqual(display._Align('abcab', 'acbd'),
                     ('abcab-', 'a-c-bd'))


if __name__ == '__main__':
  unittest.main()
