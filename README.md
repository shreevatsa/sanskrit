sanskrit/metrical-scan
======================

Code to recognize Sanskrit metres.

Web version currently serving at http://sanskritmetres.appspot.com/

Attempts to identifies metre of Sanskrit verse.

(Data, Input) → Read–Scan–Identify–Display

Given a verse,

    0. [Read] The verse is cleaned up and transliterated into SLP1.

    1. [Scan] The verse is analysed for laghu and guru syllables, and converted
    into a "metrical pattern" that might look like this:

        GGLGGLLGLGL
        GGLGGLLGLGG
        LGLGGLLGLGG
        GGLGGLLGLGG

    2. [Identify] This metrical pattern is compared against the known metrical
    patterns, and some possible best-guess metre(s) is/are found.

    3. [Display] The result is displayed, along with how the verse
    fits the metre, and (TODO) information about the metre.

--------------------------------------------------------------------------------

Simple usage from code:

   import simple_identifier
   identifier = simple_identifier.SimpleIdentifier()
   match_results = identifier.IdentifyFromLines(verse_lines)

returns a list of MatchResults that the verse might be in.

Notes:

1. The reason for using `verse_lines` as input, rather than a string that is a
single blob of text, is to enable detection of partial matches: if there are
metrical errors in the verse, but some lines are in some metre, then that metre
could still be recognized.

(Actually we do this automatically even when the line breaks aren't correctly
given, by breaking the verse into halves and quarters.)

2. Similarly, the reason for returning a list of results is that we sometimes
have multiple metres guessed, such as when different lines are in different
metres.

--------------------------------------------------------------------------------

Code organization
-----------------

![Dependency graph](deps.png?raw=true "Generated with Snakefood and DOT, see deps.sh")

### Step 0 [Read]

Covered by handle_input.py and its dependencies.

Detecting the transliteration format of the input, removing junk characters that
are not part of the verse, and transliterating the input to SLP1 (the encoding
we use internally).

### Step 1 [Scan]

Determining the pattern of gurus and laghus.

The functions in scan.py take this cleaned-up verse, and convert it to a pattern
of laghus and gurus. A "pattern" means a sequence over the alphabet {'L', 'G'}.


### Step 2 [Identify]

Match this pattern with known metres.

#### Identification algorithm.

    Given a verse,

        1. Look for the full verse's pattern in `known_metre_patterns`.

        2. Loop through `known_metre_regexes` and see if any match the full
           verses's pattern.

        3. Look in `known_partial_patterns` (then `known_partial_regexes`) for:
            -- whole verse,
            -- each line,
            -- each half,
            -- each quarter.

        4. [TODO/Maybe] Look for substrings, find closest match, etc.?
           Would have to restrict to the popular metres on the web version.

#### Metrical data.

    * A "pattern" means a sequence over the alphabet {'L', 'G'}.
    * A "regex" (for us) is a regular expression that matches some patterns.

    We use the following data structures:
    * `known_metre_patterns`, a dict mapping a pattern to a MatchResult.
    * `known_metre_regexes', a list of pairs (regex, MatchResult).
    * `known_partial_patterns`, a dict mapping a pattern to `MatchResult`s.
    * `known_partial_regexes`, a list of pairs (regex, MatchResult).

     A MatchResult is usually arrived at by looking at a pattern (or list of
     patterns), and can be seen as a tuple (metre_name, match_type):

     metre_name - name of the metre,
     match_type - used to distinguish between matching one pāda (quarter) or one
                  ardha (half) of a metre. Or, in ardha-sama metres, it can
                  distinguish between odd and even pādas.


### Step 3. [Display]

Display the list of metres found as possible guesses. For vrtta metres, we also
try to "align" the input verse to the metre, so that it's more clear where to
break it, etc. (And when the input verse has metrical errors, it's clear what
they are.)

TODO: Also, information about the metre.
