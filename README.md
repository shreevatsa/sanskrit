sanskrit/metrical-scan
======================

Code to recognize Sanskrit metres.

Given a Sanskrit verse,

    0. [Read] The verse is cleaned up and transliterated into a standard format.

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

(The reason for using verse_lines as input, rather than a single blob of text,
is to enable detection of partial matches: if there are metrical errors in the
verse, but some lines are in some metre, then that metre could still be
recognized.)

Similarly, the point of returning a list of results is to cover the case where
there might be different results, say different lines in different metres.
(This has so far been seen only with the well-known upajāti etc. mixtures.)

--------------------------------------------------------------------------------

Code organization
-----------------

![Dependency graph](deps.png?raw=true "Generated with Snakefood and DOT, see deps.sh")

### Step 0 [Read]

Covered by handle_input.py and its dependencies.

Detecting the transliteration format of the input, transliterating the input to
SLP1 (the encoding we use internally), and removing junk characters.

Also at a similar level are the functions in handle_input.py: they take care of
input, transliteration, removing things that are not part of the verse, and
finally giving the actual verse in SLP1 format.

### Step 1 [Scan]

Determining the pattern of gurus and laghus.

The functions in sscan.py take this cleaned-up verse, identify laghus-and-gurus
in it, and match it with the `known_metres` (failing that, `known_patterns` on
each line) from metrical_data.py.

### Step 2 [Identify]

The code and data are organized as follows.

At the lowest level are the functions / data structures in metrical_data.py.

    * A "pattern" means a sequence over the alphabet {'L', 'G'}.
    * A "regex" (for us) is a regular expression that matches some patterns.

    We use the following data structures:
    * `known_metre_regexes', a list of pairs (regex, MatchResult).
    * `known_metre_patterns`, a dict mapping a pattern to a MatchResult.
    * `known_partial_regexes`, a list of pairs (regex, MatchResult).
    * `known_partial_patterns`, a dict mapping a pattern to a MatchResult.

    (All of these map to just a single MatchResult, not a list of them, because
     it doesn't make sense to have multiple metres for the same line / verse.)

     A MatchResult is usually arrived at by looking at a pattern (or list of
     patterns), and can be seen as a tuple (metre_name, match_type, issues):

     metre_name - name of the metre,
     match_type - used to distinguish between matching one pāda (quarter) or one
                  ardha (half) of a metre. Or, in ardha-sama metres, it can
                  distinguish between odd and even pādas.
     issues     - E.g. pādānta-laghu, i.e. whether the pāda's final guru is
                  instead laghu in this particular sequence.


#### Identification algorithm.

    Given a verse,

        1. Look in `known_metre_patterns`.
        2. Loop through `known_metre_regexes`.
        3. Look in `known_partial_patterns` (and then loop through
        `known_partial_regexes`) for:
            -- whole verse,
            -- each half (if verse is 4 lines),
            -- each line.
        4. [Maybe] Look for substrings, find closest match, etc.?
           Would have to restrict to the popular metres on the web version.

