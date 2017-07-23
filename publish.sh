#!/bin/sh
set -eu

./clean.sh
python3 setup.py sdist
python3 setup.py bdist_wheel
twine upload -r pypi dist/*

