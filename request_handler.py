"""The web interface."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import cgi

import webapp2

import sscan


def InputForm(default=''):
  return """
    <form action="/identify" method="post">
      <div><textarea name="input_verse" rows="6" cols="80">%s</textarea></div>
      <div><input type="submit" value="Identify verse"></div>
    </form>""" % cgi.escape(default)


MAIN_PAGE_HTML = open('main.html').read().replace('${INPUT_FORM}', InputForm())

class InputPage(webapp2.RequestHandler):
  def get(self):
    self.response.write(MAIN_PAGE_HTML)


class IdentifyPage(webapp2.RequestHandler):
  def get(self):
    self.response.write(MAIN_PAGE_HTML)

  def post(self):
    """What to do with the posted input string (verse)."""
    input_verse = self.request.get('input_verse')

    identifier = sscan.Identifier()
    metre = identifier.IdentifyFromLines(input_verse.split('\n'))

    self.response.write('<html><body>')
    self.response.write('<p>')
    self.response.write(InputForm(input_verse))
    self.response.write('</p>')

    if metre:
      self.response.write('<p>The metre is <font size="+2">%s</font>' % metre)
      self.response.write('<hr/>')

    self.response.write('<p><i>Debugging output:</i></p>')
    self.response.write('<pre>')
    if metre:                             # else the debug output already has it
      self.response.write('\n'.join(identifier.cleaned_output))
    self.response.write(identifier.AllDebugOutput())
    self.response.write('</pre></body></html>')


application = webapp2.WSGIApplication([
    ('/', InputPage),
    ('/identify', IdentifyPage),
], debug=True)
