"""Utils to clean up input."""

import re


def MassageHK(text):
  """Rewrite keeping metre intact (multiple characters -> single char)."""
  # Two-letter vowels like ai and au
  text = re.sub('lR', 'R', text)
  text = re.sub('lRR', 'RR', text)
  text = re.sub('RR', 'e', text)
  text = re.sub('a[iu]', 'e', text)
  # Two-letter consonants: replace 'kh' by 'k', etc.
  alpaprana = '[kgcjTDtdpb]'
  text = re.sub('(' + alpaprana + ')' + 'h', r'\g<1>', text)
  return text


def CleanHK(text):
  """Remove non-HK characters from a block of text."""
  valid_hk = 'aAiIuUReoMHkgGcjJTDNtdnpbmyrlvzSsh'
  bad_indices = set(bad_match.start() for bad_match in
                    re.finditer('[^%s]' % valid_hk, text))
  if bad_indices:
    print 'Unknown non-HK characters are ignored:'
    print text
    print ''.join('^' if i in bad_indices else ' ' for i in range(len(text)))
    text = re.sub('[^%s]' % valid_hk, '', text)
  assert not re.search('[^%s]' % valid_hk, text), text
  return text


