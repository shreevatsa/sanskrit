sfood --internal $(find . -iname '*.py' ! -path '*_test.py') --ignore-unused | sfood-graph | dot -Tsvg > deps.svg
# Snakefood
