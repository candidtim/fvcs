#!/bin/bash

set -e

rm -rf .fvcs
poetry run fv init

echo "first line" > file.txt
echo "second line" >> file.txt
poetry run fv add file.txt
cat .fvcs/tree/file.txt/1.diff

poetry run fv diff file.txt

echo "third line" >> file.txt
poetry run fv diff file.txt
poetry run fv update file.txt
cat .fvcs/tree/file.txt/2.diff

poetry run fv restore file.txt 1
poetry run fv diff file.txt
