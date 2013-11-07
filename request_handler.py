"""The class that actually handles the input verse."""

from __future__ import unicode_literals

import cgi
import StringIO
import sys

import webapp2

import sscan

MAIN_PAGE_HTML = """\
<html>
  <body>
    <p>
      Type a Sanskrit verse into the box below and click the button.
      <br/>
      (The input can be in either Devanagari, IAST, Harvard-Kyoto, or
      ITRANS format.)
    </p>

    <form action="/identify" method="post">
      <div><textarea name="input_verse" rows="6" cols="80"></textarea></div>
      <div><input type="submit" value="Identify verse"></div>
    </form>
    <p>
    This is all very raw. Work in progress.
    Source code at
    <a href="https://github.com/shreevatsa/sanskrit/tree/metrical-scan"><!--
    -->https://github.com/shreevatsa/sanskrit/tree/metrical-scan</a>
    </p>

  </body>
</html>
"""


class InputPage(webapp2.RequestHandler):
  def get(self):
    self.response.write(MAIN_PAGE_HTML)


class IdentifyPage(webapp2.RequestHandler):
  def post(self):
    """What to do with the posted input string (verse)."""
    input_verse = self.request.get('input_verse')

    # TODO(shreevatsa): Get rid of this hack for capturing stdout.
    stdout_original = sys.stdout
    stdout_new = StringIO.StringIO()
    sys.stdout = stdout_new

    metre = sscan.IdentifyFromLines(input_verse.split('\n'))

    output = stdout_new.getvalue()
    sys.stdout = stdout_original

    self.response.write('<html><body>')
    if metre:
      self.response.write('<p>The metre is <font size="+2">%s</font>' % metre)
      self.response.write('<hr/>')
      self.response.write('<p><i>Debugging output:</i></p>')

    self.response.write('You wrote:<pre>')
    self.response.write(cgi.escape(input_verse))
    self.response.write('\n\n\n')
    self.response.write(output)
    self.response.write('</pre></body></html>')


application = webapp2.WSGIApplication([
    ('/', InputPage),
    ('/identify', IdentifyPage),
], debug=True)
