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


common_identifier = sscan.Identifier()


class InputPage(webapp2.RequestHandler):
  def get(self):
    self.response.write(MAIN_PAGE_HTML)


class IdentifyPage(webapp2.RequestHandler):
  def get(self):
    self.response.write(MAIN_PAGE_HTML)

  def post(self):
    """What to do with the posted input string (verse)."""
    input_verse = self.request.get('input_verse')

    identifier = common_identifier
    metre = identifier.IdentifyFromLines(input_verse.split('\n'))

    self.response.write('<html><body>')
    self.response.write('<p>')
    self.response.write(InputForm(input_verse))
    self.response.write('</p>')

    ok = False
    if metre:
      assert isinstance(metre, list)
      all_metres = set(m.MetreNameOnlyBase() for m in metre)
      if len(all_metres) == 1:
        if len(metre) == 1 and not metre[0].issues:
          ok = True
          self.response.write('<p>The metre is <font size="+2">%s</font>'
                              % metre[0])
        else:
          self.response.write('<p>The intended metre is probably '
                              '<font size="+2">%s</font>, '
                              'but there are issues.' % all_metres.pop())
      else:
        self.response.write('<p>The metre may be one of %s.' %
                            ' AND '.join(m.Name() for m in all_metres))
    else:
      self.response.write('<p>No metre recognized.</p>')

    self.response.write('<hr/>')
    self.response.write('<p><i>Debugging output:</i></p>')
    self.response.write('<pre>')
    if ok:  # else the debug output already has it
      self.response.write('\n'.join(identifier.cleaned_output))

    self.response.write(identifier.AllDebugOutput())
    self.response.write('</pre></body></html>')


application = webapp2.WSGIApplication([
    ('/', InputPage),
    ('/identify', IdentifyPage),
], debug=True)
