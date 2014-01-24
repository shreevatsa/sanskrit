# Snakefood
files=$(find . -iname '*.py' ! -path '*_test.py' ! -path './print_utils.py' ! -path './gretil_stats/generate_stats_table.py')
sfood --internal --internal ${files} --ignore-unused | sfood-graph | dot -Tsvg > deps.svg
inkscape -z -e deps.png deps.svg
rm deps.svg
