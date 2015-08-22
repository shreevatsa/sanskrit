# -*- coding: utf-8 -*-
"""Generate a HTML table out of the stats files."""

from __future__ import absolute_import, division, print_function, unicode_literals

import codecs
import glob
import json
import os.path

import print_utils


def Print(x):
  print_utils.Print(x)


known_texts = {
    'amaru_u.htm': 'Amaruśataka',
    'bhakirpu.htm': 'Bhāravi: Kirātārjunīya',
    'bhall_pu.htm': 'Bhallaṭaśataka',
    'bharst_u.htm': 'Bhartṛhari: Śatakatrakya',
    'kakumspu.htm': 'Kālidāsa: Kumārasambhava',
    'kmeghdpu.htm': 'Kālidāsa: Meghadūta',
    'kragh_pu.htm': 'Kālidāsa: Raghuvamśa',
    'maghspvu.htm': 'Māgha: Śiśupālavadha',
    'msubhs_u.htm': 'Mahā-subhāṣita-saṅgraha',
    'nkalivpu.htm': 'Nīlakaṇṭha Dīkṣita: Kaliviḍambana',
    'ramodtpu.htm': 'Rāmodantam',
    }

path_prefix = 'texts/gretil_stats/'

if __name__ == '__main__':
  names = [os.path.basename(f) for f in glob.glob(path_prefix + '*.stats')]
  names = [os.path.splitext(name)[0] for name in names]
  names.sort()
  # names = [os.path.splitext(name)[0] for name in names]
  assert names == sorted(known_texts.keys()), names

  total_count = {}
  individual_count = {}
  for name in names:
    stats_file = codecs.open(path_prefix + name + '.stats', 'r', 'utf-8')
    table = json.load(stats_file, 'utf-8')
    individual_count[name] = table
    for (metre, (count, percent)) in table.items():
      total_count[metre] = total_count.get(metre, 0) + count
  # Print(total_count)

  metres = [p[0] for
            p in sorted(total_count.items(), key=lambda x: x[1], reverse=True)]

  Print('<table border="1">')
  Print('<tr>')
  Print('  <td>Metre</td>')
  for name in names:
    Print(' <td>%s</td>' % known_texts[name])
  Print('</tr>')

  for metre in metres:
    Print('<tr>')
    Print('  <td>%s</td>' % metre)
    for name in names:
      Print('  <td>%s</td>' %
            print_utils.ToUnicode(individual_count[name].get(metre, '')))
    Print('</tr>')
  Print('</table>')
