#!/bin/bash

# Setup script for new feature definition

set -e

# check for filename
if [ -z "$1" ]; then
  echo -e "Please supply a file name for the feature definition\n"
  exit 1
fi

dir="$(dirname "${BASH_SOURCE[0]}")"
filename="$dir/../docs/features/$1"

if [ -e $filename ]; then
  echo -e "Filename already exists.  Choose another one.\n"
  exit 1
fi

cat << EOF > $filename
# [CLI/API/DB]: [TITLE]

## Goal: [...]

Context:
[DESCRIPTION]

## Prerequisites:
- 

## Process:
- 

## Testing:
- 
EOF