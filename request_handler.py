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
    </form>
    <p>""" % cgi.escape(default)


MAIN_PAGE_HTML = """\
<html>
  <body>
    <p>
      Type a Sanskrit verse into the box below and click the button.
      <br/>
      (The input can be in either Devanagari, IAST, Harvard-Kyoto, or
      ITRANS format.)
    </p>

    %s

    <p>
    This is all very raw. Work in progress.
    Source code at
    <a href="https://github.com/shreevatsa/sanskrit/tree/metrical-scan"><!--
    -->https://github.com/shreevatsa/sanskrit/tree/metrical-scan</a>
    </p>

  </body>
</html>
""" % InputForm()


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
    self.response.write(InputForm(input_verse))

    if metre:
      self.response.write('<p>The metre is <font size="+2">%s</font>' % metre)
      self.response.write('<hr/>')

    self.response.write('<p><i>Debugging output:</i></p>')
    self.response.write('<pre>')
    self.response.write('\n'.join(identifier.cleaned_output))
    self.response.write(identifier.AllDebugOutput())
    self.response.write('</pre></body></html>')


application = webapp2.WSGIApplication([
    ('/', InputPage),
    ('/identify', IdentifyPage),
], debug=True)
