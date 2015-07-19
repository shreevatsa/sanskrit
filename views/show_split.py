# -*- coding: utf-8 -*-

"""Show the original text and how it was split into verses.

The assumption is that each word in each verse occurs as a contiguous word in the original text.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from google.appengine.ext.webapp import template
import logging
import urllib2
import webapp2


import read.split_gretil


class ShowBlocks(webapp2.RequestHandler):
  """Given either a file or a url, retrieves text and splits into verses."""
  def get(self):
    out = template.render('templates/split.html', {})
    self.response.write(out)

  def post(self):
    """Handles post: either a file is uploaded or a url."""
    blocks = []
    action = self.request.POST.get('submit_action')
    assert action in ['Upload', 'Retrieve'], action
    if action == 'Upload':
      uploaded_file = self.request.POST.get('uploaded_htm_file')
      text = uploaded_file.file.read().decode('utf8')
    else:
      try:
        url = self.request.POST.get('url_of_htm_file')
        text = urllib2.urlopen(url).read().decode('utf8')
      except Exception as error: # pylint: disable=broad-except
        logging.error(error)
        return self.get()

    if not text:
      return self.get()

    (verses, text) = read.split_gretil.split(text)
    blocks = list(read.split_gretil.blocks_of_verses_in_text(verses, text))

    out = template.render('templates/split.html', {'blocks': blocks})
    self.response.write(out)
