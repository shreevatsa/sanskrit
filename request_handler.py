"""The web interface."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import cgi
import codecs

import webapp2

import sscan


def InputForm(default=''):
  return """
    <form action="/identify" method="post">
      <div><textarea name="input_verse" rows="6" cols="80">%s</textarea></div>
      <div><input type="submit" value="Identify verse"></div>
    </form>""" % cgi.escape(default)


def StatsTable():
  return codecs.open('stats_table.html', 'r', 'utf-8').read()


MAIN_PAGE_HTML = open('main.html').read()
MAIN_PAGE_HTML = MAIN_PAGE_HTML.replace('${INPUT_FORM}', InputForm())
MAIN_PAGE_HTML = MAIN_PAGE_HTML.replace('${METRE_STATISTICS}', StatsTable())


CommonIdentifier = sscan.Identifier()


class InputPage(webapp2.RequestHandler):
  def get(self):
    self.response.write(MAIN_PAGE_HTML)


class IdentifyPage(webapp2.RequestHandler):
  def get(self):
    self.response.write(MAIN_PAGE_HTML)

  def post(self):
    """What to do with the posted input string (verse)."""
    input_verse = self.request.get('input_verse')

    identifier = CommonIdentifier  # sscan.Identifier()
    metre = identifier.IdentifyFromLines(input_verse.split('\n'))

    self.response.write('<html><body>')
    self.response.write('<p>')
    self.response.write(InputForm(input_verse))
    self.response.write('</p>')

    if metre:
      if isinstance(metre, list):
        all_metres = set(m.MetreNameOnlyBase() for m in metre)
        if len(all_metres) == 1:
          self.response.write('<p>The intended metre is probably '
                              '<font size="+2">%s</font>, '
                              'but there are issues.' % all_metres.pop())
        else:
          metre = None
      else:
        self.response.write('<p>The metre is <font size="+2">%s</font>' % metre[0])
      self.response.write('<hr/>')

    self.response.write('<p><i>Debugging output:</i></p>')
    self.response.write('<pre>')
    if metre or isinstance(metre, list):  # else the debug output already has it
      self.response.write('\n'.join(identifier.cleaned_output))
    self.response.write(identifier.AllDebugOutput())
    self.response.write('</pre></body></html>')


application = webapp2.WSGIApplication([
    ('/', InputPage),
    ('/identify', IdentifyPage),
], debug=True)
