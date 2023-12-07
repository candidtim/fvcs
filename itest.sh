#!/bin/bash

set -e
set -x

echo "======================================================="
echo "           CLEAN AND CREATE A NEW REPOSITORY"
echo "======================================================="
rm -rf .fvcs
poetry run fv init

echo "======================================================="
echo "                   ADD A NEW FILE"
echo "======================================================="
echo "first line" > file.txt
echo "second line" >> file.txt
poetry run fv add file.txt

echo "======================================================="
echo "              CONTROL REPOSITORY STATE"
echo "======================================================="
cat .fvcs/tree/file.txt/latest
cat .fvcs/tree/file.txt/versions/*.diff | echo "no diffs"

echo "======================================================="
echo "                 CONTROL EMPTY DIFF"
echo "======================================================="
poetry run fv diff file.txt

echo "======================================================="
echo "                 MODIFY THE FILE"
echo "======================================================="
echo "third line" >> file.txt
poetry run fv diff file.txt
poetry run fv update file.txt
poetry run fv log file.txt

echo "======================================================="
echo "              CONTROL REPOSITORY STATE"
echo "======================================================="
cat .fvcs/tree/file.txt/latest
cat .fvcs/tree/file.txt/versions/*.diff

echo "======================================================="
echo "              RESTORE PREVIOUS VERSION"
echo "======================================================="
poetry run fv get file.txt 1
poetry run fv diff file.txt

echo "======================================================="
echo "              CONTROL REPOSITORY STATE"
echo "======================================================="
cat .fvcs/tree/file.txt/latest
cat .fvcs/tree/file.txt/versions/*.diff

rm -f file.txt
