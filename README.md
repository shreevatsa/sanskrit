sanskrit/metrical-scan
======================

Code to recognize Sanskrit metres.

Given a Sanskrit verse,

    1. [Scan] The verse is analysed for laghu and guru syllables, and converted
    into a "metrical pattern" that might look like this:

        GGLGGLLGLGL
        GGLGGLLGLGG
        LGLGGLLGLGG
        GGLGGLLGLGG

    2. [Identify] This metrical pattern is compared against the known metrical
    patterns, and some best-guess metre is output.

--------------------------------------------------------------------------------

From a user point of view, class Identifier in sscan.py is all that needs to be
interacted with. If `identifer` is an instance of `Identifier`, then

    identifier.IdentifyFromLines(verse_lines)

returns a list of MatchResults that the verse might be in.

(The reason for using verse_lines rather than a single blob of text is to enable
detection of partial matches: if there are metrical errors in the verse, but
some lines are in metre, then they could still be recognized..)

Similarly, the point of returning a list of results is to cover the case where
there might be different results, say different lines in different metres.
(This has so far been seen only with the well-known upajāti etc. mixtures.)

--------------------------------------------------------------------------------

Step 1 [Scan] involves detecting the transliteration format of the input,
transliterating it to SLP1 (the encoding we use internally), removing junk
characters, and looking at the pattern of gurus and laghus.

For Step 2 [Identify], the code and data are organized as follows.

At the lowest level are the functions / data structures in metrical_data.py.

  * `known_patterns`: a dict mapping a sequence over the alphabet {'L', 'G'} to
    a list of `MatchResult`s.

     A MatchResult can be seen as a tuple (metre_name, match_type, issues):
     metre_name - name of the metre,
     match_type - used to distinguish between matching one pāda (quarter) or one
     		  ardha (half) of a metre. Or, in ardha-sama metres, it can
     		  distinguish between odd and even pādas.
     issues	- E.g. pādānta-laghu, i.e. whether the pāda's final guru is
     		  instead laghu in this particular sequence.

  * `known_metres`: a dict mapping a regex (as of now, just a string over the
     alphabet {'.', 'L', G'}) to a `MatchResult`.
     (Just a single MatchResult, not a list, because it doesn't make sense to
     have multiple metres for the same verse.)
          The match_type in these MatchResults is always a full verse.
     	  The issues can be things like viṣama-pādānta-laghu, or "off" pādas.

Also at a similar level are the functions in handle_input.py: they take care of
input, transliteration, removing things that are not part of the verse, and
finally giving the actual verse in SLP1 format.

Finally, the functions in sscan.py take this cleaned-up verse, identify
laghus-and-gurus in it, and match it with the `known_metres` (failing that,
`known_patterns` on each line) from metrical_data.py.

--------------------------------------------------------------------------------

Redesign.

Data structures.
    * `known_metre_patterns`, a dict mapping a pattern to a MatchResult.
    * `known_metre_regexes', a list of pairs (regex, MatchResult)
    * `known_partial_patterns`, a dict mapping a pattern to a MatchResult.

Identification algorithm.
    Given a verse,
        1. Look in known_metre_patterns.
        2. Loop through known_metre_regexes.
        3. Look in known_partial_patterns for:
            -- whole verse,
            -- each half (if verse is 4 lines),
            -- each line.
        4. [Maybe] Look for substrings, find closest match, etc.?
           Would have to restrict to the popular metres on the web version.

