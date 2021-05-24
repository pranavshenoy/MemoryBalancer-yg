#!/bin/sh
set -o errexit -o xtrace

DIR=$1
TIME=$(date +%s)

last=`ls "$1" | sort -r | head -1`
python3 python/plot.py "$1/$last"
scp plot.png "uwplse.org:/var/www/membalancer/$TIME.png"

if command -v nightly-results &>/dev/null; then
    nightly-results img https://membalancer.uwplse.org/$TIME.png
fi
