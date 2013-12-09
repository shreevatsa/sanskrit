sanskrit/metrical-scan
======================

Code to recognize metre given a Sanskrit verse.

The code and data are organized as follows.

At the lowest level are the functions / data structures in metrical_data.py.

   * known_patterns: a dict mapping sequence of LGs to list of `MetrePattern`s.
     A MetrePattern can be seen as a tuple (metre_name, match_type, issues).
     Here match_type is used to distinguish between matching one pāda (quarter)
     or one ardha (half) of a metre.

   * known_metres is a dict mapping a regex (usually over alphabet '.LG') to a
     MetrePattern. The match_type here is always a full verse. It doesn't make
     sense to have multiple MetrePatterns for the exact same metre.

