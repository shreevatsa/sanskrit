#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for display."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

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
    # display.AlignVerseToMetre(
    #   ['asahyaM tvasAdhyaM ca bANIyavANyAH punArUpaNaM tvanyavANISu pUrNam .'
    #    'itIdaM mahAvAraNaM vArayantaM tvadIyaM prayatnaM stuvehaM kathaM vA'],
    #   'Bhujañgaprayātam', '')


if __name__ == '__main__':
  unittest.main()
