#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tries to identify metre of given verse lines.

Usage from commandline:
     python sscan.py
     [input verse]
     Ctrl-D

     or

     python sscan.py < input_file

Known issues:
     See https://github.com/shreevatsa/sanskrit/issues?state=open
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import sys

import print_utils
import identifier_pipeline


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.WARNING)
  from_stdin = sys.stdin.read().decode('utf8')
  identifier = identifier_pipeline.IdentifierPipeline()
  identifier.IdentifyFromText(from_stdin)
  print_utils.Print(identifier.AllDebugOutput())
