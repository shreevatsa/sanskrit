# Needs to be run from the top-level directory (the one that contains texts/, etc.)
function scan() {
  if [ -f texts/gretil_stats/diff-$1.htm.patch ];
    then
      patch ~/GRETIL/forme/$1.htm -o /tmp/$1.htm < texts/gretil_stats/diff-$1.htm.patch
  else
      cp ~/GRETIL/forme/$1.htm /tmp/$1.htm
  fi
  python -m texts.read_gretil /tmp/$1.htm --print_identified_verses=none --print_unidentified_verses=none
  mv $1.htm.stats texts/gretil_stats/
}

# Lots of footnotes etc. to remove in these yet.
scan amaru_u
scan bhakirpu
scan bhall_pu
python -m texts.read_gretil texts/gretil_stats/bharst_u.htm --print_identified_verses=none --print_unidentified_verses=none && mv bharst_u.htm.stats texts/gretil_stats
scan kakumspu
scan kragh_pu
scan maghspvu
scan msubhs_u
scan nkalivpu
scan ramodtpu

python -m texts.gretil_stats.generate_stats_table > texts/gretil_stats/stats_table.html