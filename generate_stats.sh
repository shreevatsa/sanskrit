patch ~/GRETIL/forme/amaru_u.htm -o /tmp/amaru_u.htm < diff-amaru_u.htm.patch && ./read_gretil.py /tmp/amaru_u.htm
./read_gretil.py ~/GRETIL/forme/bhakirpu.htm
./read_gretil.py ~/GRETIL/forme/bhall_xu.htm
./read_gretil.py bharst_u.htm
./read_gretil.py ~/GRETIL/forme/kakumspu.htm
./read_gretil.py ~/GRETIL/forme/kragh_pu.htm
./read_gretil.py ~/GRETIL/forme/maghspvu.htm
patch ~/GRETIL/forme/meghdk_u.htm -o /tmp/meghdk_u.htm < diff-meghdk_u.htm.patch && ./read_gretil.py /tmp/meghdk_u.htm
./read_gretil.py ~/GRETIL/forme/msubhs_u.htm
./read_gretil.py ~/GRETIL/forme/nkalivxu.htm
patch ~/GRETIL/forme/ramodtpu.htm -o /tmp/ramodtpu.htm < diff-ramodtpu.htm.patch && ./read_gretil.py /tmp/ramodtpu.htm
python generate_stats_table.py > stats_table.html
