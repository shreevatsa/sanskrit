# Snakefood
sfood --internal $(find . -iname '*.py' ! -path '*_test.py') --ignore-unused | sfood-graph | dot -Tpng > deps.png
