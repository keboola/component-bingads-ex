#!/bin/sh
set -e

flake8
python -m unittest discover