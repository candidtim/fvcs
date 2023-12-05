#!/bin/bash

set -e
set -x

rm -rf .fvcs
poetry run fv init

echo "first line" > file.txt
echo "second line" >> file.txt
poetry run fv add file.txt
cat .fvcs/tree/file.txt/latest
cat .fvcs/tree/file.txt/*.diff | echo "no diffs"

poetry run fv diff file.txt

echo "third line" >> file.txt
poetry run fv diff file.txt
poetry run fv update file.txt
cat .fvcs/tree/file.txt/latest
cat .fvcs/tree/file.txt/*.diff

poetry run fv restore file.txt -v 1
poetry run fv diff file.txt
