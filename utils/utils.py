# -*- coding: utf-8 -*-

"""General-purpose utils."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import logging


def call_with_log_capture(function, *args, **kwargs):
  """Call the function with args and kwargs, and return both its result and logging."""
  logger = logging.getLogger()
  # NOTE: logger.level, logger.handlers, handler.level are all undocumented API.
  original_logger_level = logger.level
  original_handler_levels = [handler.level for handler in logger.handlers]
  for handler in logger.handlers:
    handler.setLevel(max(handler.level, original_logger_level))
  logger.setLevel(logging.DEBUG)
  log_capturer_stream = io.StringIO()
  log_capture_handler = logging.StreamHandler(log_capturer_stream)
  log_capture_handler.setLevel(logging.DEBUG)
  logger.addHandler(log_capture_handler)

  return_value = function(*args, **kwargs)

  log_contents = log_capturer_stream.getvalue()
  log_capturer_stream.close()
  logger.removeHandler(log_capture_handler)
  for (i, handler) in enumerate(logger.handlers):
    handler.setLevel(original_handler_levels[i])
  logger.setLevel(original_logger_level)

  if log_contents:
    assert log_contents[-1] == '\n'
    log_contents = log_contents[:-1]
  return (return_value, log_contents)
