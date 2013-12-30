patch ~/GRETIL/forme/amaru_u.htm -o /tmp/amaru_u.htm < diff-amaru_u.htm.patch && ./read_gretil.py /tmp/amaru_u.htm --print_identified_verses=none
./read_gretil.py ~/GRETIL/forme/bhakirpu.htm --print_identified_verses=none
./read_gretil.py ~/GRETIL/forme/bhall_xu.htm --print_identified_verses=none
./read_gretil.py bharst_u.htm --print_identified_verses=none
./read_gretil.py ~/GRETIL/forme/kakumspu.htm --print_identified_verses=none
./read_gretil.py kragh_pu.htm --print_identified_verses=none
./read_gretil.py ~/GRETIL/forme/maghspvu.htm --print_identified_verses=none
patch ~/GRETIL/forme/meghdk_u.htm -o /tmp/meghdk_u.htm < diff-meghdk_u.htm.patch && ./read_gretil.py /tmp/meghdk_u.htm --print_identified_verses=none
./read_gretil.py ~/GRETIL/forme/msubhs_u.htm --print_identified_verses=none
patch ~/GRETIL/forme/nkalivpu.htm -o /tmp/nkalivpu.htm < diff-nkalivpu.htm.patch && ./read_gretil.py /tmp/nkalivpu.htm --print_identified_verses=none
patch ~/GRETIL/forme/ramodtpu.htm -o /tmp/ramodtpu.htm < diff-ramodtpu.htm.patch && ./read_gretil.py /tmp/ramodtpu.htm --print_identified_verses=none
python generate_stats_table.py > stats_table.html
