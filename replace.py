import os
import re

have = os.listdir('.')

def replace_href(match):
  '''Given (<a href=")(...)", rewrite the second one.'''
  assert len(match.groups()) == 2
  href = match.group(2)
  def replacement(): return match.group(1) + href + '"'
  if 'gret_utf.htm' in href:
    href = href.replace('http://gretil.sub.uni-goettingen.de/gret_utf.htm#', '#')
    href = href.replace('gret_utf.htm#', '#')
    assert href.startswith('#') or href == 'http://gretil.sub.uni-goettingen.de/gret_utf.htm'
    return replacement()
  # Links in gret_utf.htm that are not links to files
  if href.endswith('gretinfo.htm') or href.endswith('gr_elib.htm') or href.endswith('fiindole.htm'):
    return replacement()
  if not href.endswith('.htm'):
    if not ('gret_ree.htm#' in href or 'gret_csx.htm#' in href or 'gret_ati.htm#' in href or 'gretil.htm#Index' in href or 'gretinfo.htm' in href):
      print 'Ignoring non-file link: ', href
    return replacement()
  # This file appears to be missing
  if 'gretil/4_drav/tamil/pm/pm013__u.htm' in href:
    return replacement()
  # A couple of files are uppercase in the zip file
  if 'gretil/3_nia/hindi/bacmadhu.htm' in href:
    href = href.replace('bacmadhu.htm', 'BACMADHU.HTM')
  if 'gretil/1_sanskr/4_rellit/buddh/klpdraau.htm' in href:
    href = href.replace('klpdraau.htm', 'KLPDRAAU.HTM')
  # In all other cases, the file seems to be present
  filename = href[href.rfind('/') + 1 :]
  assert filename in have, 'Filename: %s, href: %s' % (filename, href)
  href = href.replace(href, filename)
  # print 'For \n%s, returning \n%s' % (match.group(0), replacement)
  return replacement()

lines = open('gret_utf.htm').readlines()
newlines = []
for line in lines:
  newstr = re.sub(r'(<a href=")([^"]*)"', replace_href, line, flags = re.IGNORECASE)
  newlines.append(newstr)

open('index.html', 'w').writelines(newlines)
    
