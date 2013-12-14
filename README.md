sanskrit/metrical-scan
======================

Code to recognize metre given a Sanskrit verse.

The code and data are organized as follows.

At the lowest level are the functions / data structures in metrical_data.py.

  * `known_patterns`: a dict mapping a sequence over the alphabet {'L', 'G'} to
    a list of `MetrePattern`s.

     A MetrePattern can be seen as a tuple (metre_name, match_type, issues):
     metre_name - name of the metre,
     match_type - used to distinguish between matching one pāda (quarter) or one
     		  ardha (half) of a metre. Or, in ardha-sama metres, it can
     		  distinguish between odd and even pādas.
     issues	- E.g. pādānta-laghu, i.e. whether the pāda's final guru is
     		  instead laghu in this particular sequence.

  * `known_metres`: a dict mapping a regex (as of now, just a string over the
     alphabet {'.', 'L', G'}) to a `MetrePattern`.
     (Just a single MetrePattern, not a list, because it doesn't make sense to
     have multiple metres for the same verse.)
          The match_type in these MetrePatterns is always a full verse.
     	  The issues can be things like viṣama-pādānta-laghu, or "off" pādas.



