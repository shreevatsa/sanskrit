# Needs to be run from the top-level directory (the one that contains texts/, etc.)
function scan() {
  if [ -f texts/gretil_stats/diff-$1.htm.patch ];
    then
      patch ~/GRETIL/forme/$1.htm -o /tmp/$1.htm < texts/gretil_stats/diff-$1.htm.patch
  elif [ -f texts/gretil_stats/$1.htm ];
    then
      cp texts/gretil_stats/$1.htm /tmp/$1.htm
  else
      cp ~/GRETIL/forme/$1.htm /tmp/$1.htm
  fi
  python -m texts.read_gretil /tmp/$1.htm --print_identified_verses=none --print_unidentified_verses=none
  mv $1.htm.stats texts/gretil_stats/
}

# Every verse perfectly metrical
scan nkalivpu
scan ramodtpu
scan kmeghdpu

# Some "probably"s
scan amaru_u
scan bhall_pu

# Errors for sure
scan kragh_pu
scan bhakirpu
scan bharst_u
python -m texts.read_gretil texts/gretil_stats/bharst_u.htm --print_identified_verses=none --print_unidentified_verses=none && mv bharst_u.htm.stats texts/gretil_stats

# Lots of footnotes etc. to remove in these yet.
# scan kakumspu
# scan maghspvu
# scan msubhs_u

python -m texts.gretil_stats.generate_stats_table > texts/gretil_stats/stats_table.html
