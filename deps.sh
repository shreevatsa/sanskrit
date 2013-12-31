# Snakefood
sfood --internal $(find . -iname '*.py' ! -path '*_test.py') --ignore-unused | sfood-graph | dot -Tsvg > deps.svg
inkscape -z -e deps.png deps.svg
